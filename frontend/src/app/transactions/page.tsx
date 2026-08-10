'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { TransactionFormModal } from '@/components/TransactionFormModal';
import { assetsApi } from '@/lib/assets';
import { categoriesApi } from '@/lib/categories';
import { transactionsApi } from '@/lib/transactions';
import type { Asset } from '@/types/asset';
import type {
  ExpenseCategory,
  IncomeCategory,
  MajorCategory,
} from '@/types/category';
import type { MonthlySummary, Transaction } from '@/types/transaction';

function formatYen(value: string): string {
  return `¥${Number(value).toLocaleString()}`;
}

function formatDate(value: string): string {
  const [, month, day] = value.split('-');
  return `${month}/${day}`;
}

export default function TransactionsPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<MonthlySummary | null>(null);
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
    transaction?: Transaction;
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

  const loadMonthData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [transactionList, monthlySummary] = await Promise.all([
        transactionsApi.list(year, month),
        transactionsApi.monthlySummary(year, month),
      ]);
      setTransactions(transactionList.items);
      setSummary(monthlySummary);
    } catch (err) {
      setError(err instanceof Error ? err.message : '取引の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  }, [year, month]);

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
  }, [loadMasterData]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- 月切り替え時のデータ再取得
    void loadMonthData();
  }, [loadMonthData]);

  const handlePrevMonth = () => {
    if (month === 1) {
      setYear((y) => y - 1);
      setMonth(12);
    } else {
      setMonth((m) => m - 1);
    }
  };

  const handleNextMonth = () => {
    if (month === 12) {
      setYear((y) => y + 1);
      setMonth(1);
    } else {
      setMonth((m) => m + 1);
    }
  };

  const categoryPill = (transaction: Transaction) => {
    if (transaction.expense_category_id !== null) {
      const major = transaction.major_category_id
        ? majorCategoriesById.get(transaction.major_category_id)?.name
        : undefined;
      const expense = expenseCategoriesById.get(
        transaction.expense_category_id,
      )?.name;
      return (
        <span className="rounded-full bg-expense-soft px-2.5 py-0.5 text-xs text-expense">
          {major ? `${major} / ${expense ?? ''}` : expense}
        </span>
      );
    }
    if (transaction.income_category_id !== null) {
      const income = incomeCategoriesById.get(
        transaction.income_category_id,
      )?.name;
      return (
        <span className="rounded-full bg-income-soft px-2.5 py-0.5 text-xs text-income">
          {income}
        </span>
      );
    }
    return (
      <span className="rounded-full bg-tag-bg px-2.5 py-0.5 text-xs text-ink-muted">
        調整
      </span>
    );
  };

  return (
    <AppShell>
      <div className="mb-1 flex items-baseline gap-2.5">
        <h2 className="text-[17px] text-ink">取引一覧(月別)</h2>
        <span className="rounded bg-tag-bg px-1.5 py-0.5 font-mono text-[11px] text-ink-muted">
          /transactions
        </span>
      </div>

      <div className="mb-4 flex items-center gap-2.5 font-mono text-[12.5px]">
        <button
          type="button"
          className="flex h-6 w-6 items-center justify-center rounded border border-line text-ink-muted"
          onClick={handlePrevMonth}
        >
          ‹
        </button>
        <div className="text-sm font-semibold text-ink">
          {year}年{month}月
        </div>
        <button
          type="button"
          className="flex h-6 w-6 items-center justify-center rounded border border-line text-ink-muted"
          onClick={handleNextMonth}
        >
          ›
        </button>
      </div>

      {loading && <p className="text-xs text-ink-muted">読み込み中...</p>}
      {error && <p className="text-xs text-expense">{error}</p>}

      {summary && (
        <div className="mb-4.5 flex gap-2.5">
          <div className="flex-1 rounded border border-line-soft bg-paper px-3.5 py-2.5">
            <div className="font-mono text-[10.5px] tracking-wide text-ink-muted uppercase">
              収入合計
            </div>
            <div className="mt-0.5 font-mono text-lg text-income tabular-nums">
              {formatYen(summary.income_total)}
            </div>
          </div>
          <div className="flex-1 rounded border border-line-soft bg-paper px-3.5 py-2.5">
            <div className="font-mono text-[10.5px] tracking-wide text-ink-muted uppercase">
              支出合計
            </div>
            <div className="mt-0.5 font-mono text-lg text-expense tabular-nums">
              {formatYen(summary.expense_total)}
            </div>
          </div>
          <div className="flex-1 rounded border border-line-soft bg-paper px-3.5 py-2.5">
            <div className="font-mono text-[10.5px] tracking-wide text-ink-muted uppercase">
              収支差額
            </div>
            <div className="mt-0.5 font-mono text-lg text-ink tabular-nums">
              {formatYen(summary.balance)}
            </div>
          </div>
        </div>
      )}

      <div className="overflow-x-auto rounded border border-line-soft">
        <table className="w-full text-[12.5px]">
          <thead>
            <tr>
              <th className="border-b border-line px-2.5 py-1.5 text-left font-mono text-[10.5px] text-ink-muted uppercase">
                日付
              </th>
              <th className="border-b border-line px-2.5 py-1.5 text-left font-mono text-[10.5px] text-ink-muted uppercase">
                カテゴリ
              </th>
              <th className="border-b border-line px-2.5 py-1.5 text-left font-mono text-[10.5px] text-ink-muted uppercase">
                資産
              </th>
              <th className="border-b border-line px-2.5 py-1.5 text-left font-mono text-[10.5px] text-ink-muted uppercase">
                メモ
              </th>
              <th className="border-b border-line px-2.5 py-1.5 text-right font-mono text-[10.5px] text-ink-muted uppercase">
                金額
              </th>
              <th className="border-b border-line px-2.5 py-1.5"></th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((transaction) => (
              <tr
                key={transaction.id}
                className="cursor-pointer hover:bg-tag-bg/40"
                onClick={() => setFormModal({ mode: 'edit', transaction })}
              >
                <td className="border-b border-line-soft px-2.5 py-2">
                  {formatDate(transaction.date)}
                </td>
                <td className="border-b border-line-soft px-2.5 py-2">
                  {categoryPill(transaction)}
                </td>
                <td className="border-b border-line-soft px-2.5 py-2">
                  {assetsById.get(transaction.asset_id)?.name ?? ''}
                </td>
                <td className="border-b border-line-soft px-2.5 py-2 text-ink-muted">
                  {transaction.memo}
                </td>
                <td
                  className={
                    transaction.entry_kind === 'income'
                      ? 'border-b border-line-soft px-2.5 py-2 text-right font-mono text-income tabular-nums'
                      : 'border-b border-line-soft px-2.5 py-2 text-right font-mono text-expense tabular-nums'
                  }
                >
                  {transaction.entry_kind === 'income' ? '+' : '-'}
                  {formatYen(transaction.amount)}
                </td>
                <td className="border-b border-line-soft px-2.5 py-2 text-center text-ink-muted">
                  ⋯
                </td>
              </tr>
            ))}
            {transactions.length === 0 && !loading && (
              <tr>
                <td
                  colSpan={6}
                  className="px-2.5 py-4 text-center text-ink-muted"
                >
                  この月の取引はありません
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <button
        type="button"
        className="fixed right-8 bottom-8 flex h-11 w-11 items-center justify-center rounded-full bg-accent text-xl text-paper shadow-lg"
        onClick={() => setFormModal({ mode: 'create' })}
      >
        +
      </button>

      {formModal && (
        <TransactionFormModal
          mode={formModal.mode}
          initialTransaction={formModal.transaction}
          assets={assets}
          majorCategories={majorCategories}
          expenseCategories={expenseCategories}
          incomeCategories={incomeCategories}
          onClose={() => setFormModal(null)}
          onCategoriesChanged={loadMasterData}
          onSubmit={async (input) => {
            if (formModal.mode === 'create') {
              await transactionsApi.create(input);
            } else if (formModal.transaction) {
              await transactionsApi.update(formModal.transaction.id, input);
            }
            await loadMonthData();
          }}
          onDelete={
            formModal.mode === 'edit' && formModal.transaction
              ? async () => {
                  await transactionsApi.remove(formModal.transaction!.id);
                  await loadMonthData();
                }
              : undefined
          }
        />
      )}
    </AppShell>
  );
}
