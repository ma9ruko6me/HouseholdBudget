'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { RecurringTransactionFormModal } from '@/components/RecurringTransactionFormModal';
import { assetsApi } from '@/lib/assets';
import { categoriesApi } from '@/lib/categories';
import { recurringTransactionsApi } from '@/lib/recurringTransactions';
import type { Asset } from '@/types/asset';
import type {
  ExpenseCategory,
  IncomeCategory,
  MajorCategory,
} from '@/types/category';
import type { RecurringTransaction } from '@/types/recurringTransaction';

function formatYen(value: string): string {
  return `¥${Number(value).toLocaleString()}`;
}

export default function RecurringTransactionsPage() {
  const [recurringTransactions, setRecurringTransactions] = useState<
    RecurringTransaction[]
  >([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [majorCategories, setMajorCategories] = useState<MajorCategory[]>([]);
  const [expenseCategories, setExpenseCategories] = useState<ExpenseCategory[]>(
    [],
  );
  const [incomeCategories, setIncomeCategories] = useState<IncomeCategory[]>(
    [],
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formModal, setFormModal] = useState<{
    mode: 'create' | 'edit';
    recurringTransaction?: RecurringTransaction;
  } | null>(null);

  const assetsById = useMemo(
    () => new Map(assets.map((a) => [a.id, a])),
    [assets],
  );
  const majorCategoriesById = useMemo(
    () => new Map(majorCategories.map((c) => [c.id, c])),
    [majorCategories],
  );
  const expenseCategoriesById = useMemo(
    () => new Map(expenseCategories.map((c) => [c.id, c])),
    [expenseCategories],
  );
  const incomeCategoriesById = useMemo(
    () => new Map(incomeCategories.map((c) => [c.id, c])),
    [incomeCategories],
  );

  const loadRecurringTransactions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await recurringTransactionsApi.list();
      setRecurringTransactions(result.items);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : '定期取引の取得に失敗しました',
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const loadMasterData = useCallback(async () => {
    const [assetList, majors, expenseCats, incomeCats] = await Promise.all([
      assetsApi.list(),
      categoriesApi.listMajorCategories(),
      categoriesApi.listExpenseCategories(),
      categoriesApi.listIncomeCategories(),
    ]);
    setAssets(assetList.items);
    setMajorCategories(majors);
    setExpenseCategories(expenseCats);
    setIncomeCategories(incomeCats);
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- 初回マウント時のデータ取得
    void loadMasterData();
    void loadRecurringTransactions();
  }, [loadMasterData, loadRecurringTransactions]);

  const categoryCells = (recurring: RecurringTransaction) => {
    if (recurring.expense_category_id !== null) {
      const major = recurring.major_category_id
        ? majorCategoriesById.get(recurring.major_category_id)?.name
        : undefined;
      const expense = expenseCategoriesById.get(
        recurring.expense_category_id,
      )?.name;
      return { major: major ?? '', mid: expense ?? '' };
    }
    if (recurring.income_category_id !== null) {
      const income = incomeCategoriesById.get(
        recurring.income_category_id,
      )?.name;
      return { major: '', mid: income ?? '' };
    }
    return { major: '', mid: '' };
  };

  return (
    <AppShell>
      <div className="mb-1 flex items-baseline gap-2.5">
        <h2 className="text-[17px] text-ink">定期取引管理</h2>
        <span className="rounded bg-tag-bg px-1.5 py-0.5 font-mono text-[11px] text-ink-muted">
          /recurring-transactions
        </span>
      </div>
      <p className="mb-4.5 max-w-[70ch] text-[12.5px] text-ink-muted">
        毎月発生する取引を登録しておくと、該当日になったら自動的に取引として登録される。
      </p>

      {loading && <p className="text-xs text-ink-muted">読み込み中...</p>}
      {error && <p className="text-xs text-expense">{error}</p>}

      <div className="overflow-x-auto rounded border border-line-soft">
        <table className="w-full text-[12.5px]">
          <thead>
            <tr>
              <th className="border-b border-line px-2.5 py-1.5 text-left font-mono text-[10.5px] text-ink-muted uppercase">
                大カテゴリ
              </th>
              <th className="border-b border-line px-2.5 py-1.5 text-left font-mono text-[10.5px] text-ink-muted uppercase">
                中カテゴリ
              </th>
              <th className="border-b border-line px-2.5 py-1.5 text-left font-mono text-[10.5px] text-ink-muted uppercase">
                資産
              </th>
              <th className="border-b border-line px-2.5 py-1.5 text-left font-mono text-[10.5px] text-ink-muted uppercase">
                頻度
              </th>
              <th className="border-b border-line px-2.5 py-1.5 text-left font-mono text-[10.5px] text-ink-muted uppercase">
                登録日
              </th>
              <th className="border-b border-line px-2.5 py-1.5 text-right font-mono text-[10.5px] text-ink-muted uppercase">
                金額
              </th>
              <th className="border-b border-line px-2.5 py-1.5"></th>
            </tr>
          </thead>
          <tbody>
            {recurringTransactions.map((recurring) => {
              const { major, mid } = categoryCells(recurring);
              return (
                <tr
                  key={recurring.id}
                  className="cursor-pointer hover:bg-tag-bg/40"
                  onClick={() =>
                    setFormModal({
                      mode: 'edit',
                      recurringTransaction: recurring,
                    })
                  }
                >
                  <td className="border-b border-line-soft px-2.5 py-2">
                    {major}
                  </td>
                  <td className="border-b border-line-soft px-2.5 py-2">
                    {mid || recurring.name}
                  </td>
                  <td className="border-b border-line-soft px-2.5 py-2">
                    {assetsById.get(recurring.asset_id)?.name ?? ''}
                  </td>
                  <td className="border-b border-line-soft px-2.5 py-2 text-ink-muted">
                    毎月
                  </td>
                  <td className="border-b border-line-soft px-2.5 py-2">
                    毎月{recurring.day_of_month}日
                  </td>
                  <td
                    className={
                      recurring.entry_kind === 'income'
                        ? 'border-b border-line-soft px-2.5 py-2 text-right font-mono text-income tabular-nums'
                        : 'border-b border-line-soft px-2.5 py-2 text-right font-mono text-expense tabular-nums'
                    }
                  >
                    {recurring.entry_kind === 'income' ? '+' : '-'}
                    {formatYen(recurring.amount)}
                  </td>
                  <td className="border-b border-line-soft px-2.5 py-2 text-center text-ink-muted">
                    ✎
                  </td>
                </tr>
              );
            })}
            {recurringTransactions.length === 0 && !loading && (
              <tr>
                <td
                  colSpan={7}
                  className="px-2.5 py-4 text-center text-ink-muted"
                >
                  定期取引は登録されていません
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4">
        <button
          type="button"
          className="rounded border border-accent bg-accent px-3 py-1.5 font-mono text-[11.5px] text-paper"
          onClick={() => setFormModal({ mode: 'create' })}
        >
          + 定期取引を追加
        </button>
      </div>

      {formModal && (
        <RecurringTransactionFormModal
          mode={formModal.mode}
          initialRecurringTransaction={formModal.recurringTransaction}
          assets={assets}
          majorCategories={majorCategories}
          expenseCategories={expenseCategories}
          incomeCategories={incomeCategories}
          onClose={() => setFormModal(null)}
          onCategoriesChanged={loadMasterData}
          onSubmit={async (input) => {
            if (formModal.mode === 'create') {
              await recurringTransactionsApi.create(input);
            } else if (formModal.recurringTransaction) {
              await recurringTransactionsApi.update(
                formModal.recurringTransaction.id,
                input,
              );
            }
            await loadRecurringTransactions();
          }}
          onDelete={
            formModal.mode === 'edit' && formModal.recurringTransaction
              ? async () => {
                  await recurringTransactionsApi.remove(
                    formModal.recurringTransaction!.id,
                  );
                  await loadRecurringTransactions();
                }
              : undefined
          }
        />
      )}
    </AppShell>
  );
}
