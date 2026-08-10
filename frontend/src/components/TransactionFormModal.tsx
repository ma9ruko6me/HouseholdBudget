'use client';

import { useMemo, useState, type FormEvent } from 'react';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { categoriesApi } from '@/lib/categories';
import type { Asset } from '@/types/asset';
import type {
  ExpenseCategory,
  IncomeCategory,
  MajorCategory,
} from '@/types/category';
import type {
  EntryKind,
  Transaction,
  TransactionInput,
} from '@/types/transaction';

type Props = {
  mode: 'create' | 'edit';
  initialTransaction?: Transaction;
  assets: Asset[];
  majorCategories: MajorCategory[];
  expenseCategories: ExpenseCategory[];
  incomeCategories: IncomeCategory[];
  onSubmit: (input: TransactionInput) => Promise<void>;
  onDelete?: () => Promise<void>;
  onCategoriesChanged: () => Promise<void>;
  onClose: () => void;
};

export function TransactionFormModal({
  mode,
  initialTransaction,
  assets,
  majorCategories,
  expenseCategories,
  incomeCategories,
  onSubmit,
  onDelete,
  onCategoriesChanged,
  onClose,
}: Props) {
  const [date, setDate] = useState(
    initialTransaction?.date ?? new Date().toISOString().slice(0, 10),
  );
  const [entryKind, setEntryKind] = useState<EntryKind>(
    initialTransaction?.entry_kind ?? 'expense',
  );
  const [majorCategoryId, setMajorCategoryId] = useState<number | null>(
    initialTransaction?.major_category_id ?? majorCategories[0]?.id ?? null,
  );
  const [expenseCategoryId, setExpenseCategoryId] = useState<number | null>(
    initialTransaction?.expense_category_id ?? null,
  );
  const [incomeCategoryId, setIncomeCategoryId] = useState<number | null>(
    initialTransaction?.income_category_id ?? null,
  );
  const [assetId, setAssetId] = useState<number | null>(
    initialTransaction?.asset_id ?? assets[0]?.id ?? null,
  );
  const [transferToAssetId, setTransferToAssetId] = useState<number | null>(
    initialTransaction?.transfer_to_asset_id ?? null,
  );
  const [amount, setAmount] = useState(initialTransaction?.amount ?? '');
  const [memo, setMemo] = useState(initialTransaction?.memo ?? '');
  const [addingCategory, setAddingCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState<{
    kind: 'expense' | 'income';
    id: number;
    name: string;
  } | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const visibleExpenseCategories = useMemo(
    () =>
      expenseCategories.filter((c) => c.major_category_id === majorCategoryId),
    [expenseCategories, majorCategoryId],
  );

  const handleToggleKind = (kind: EntryKind) => {
    setEntryKind(kind);
    setAddingCategory(false);
    if (kind === 'expense') {
      setIncomeCategoryId(null);
      setTransferToAssetId(null);
      setMajorCategoryId(
        (current) => current ?? majorCategories[0]?.id ?? null,
      );
    } else if (kind === 'income') {
      setMajorCategoryId(null);
      setExpenseCategoryId(null);
      setTransferToAssetId(null);
    } else {
      setMajorCategoryId(null);
      setExpenseCategoryId(null);
      setIncomeCategoryId(null);
    }
  };

  const handleSelectMajorCategory = (id: number) => {
    setMajorCategoryId(id);
    setExpenseCategoryId(null);
  };

  const handleAddCategory = async () => {
    const name = newCategoryName.trim();
    if (!name) return;
    try {
      if (entryKind === 'expense') {
        if (majorCategoryId === null) return;
        const created = await categoriesApi.createExpenseCategory(
          majorCategoryId,
          name,
        );
        await onCategoriesChanged();
        setExpenseCategoryId(created.id);
      } else {
        const created = await categoriesApi.createIncomeCategory(name);
        await onCategoriesChanged();
        setIncomeCategoryId(created.id);
      }
      setNewCategoryName('');
      setAddingCategory(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'カテゴリの追加に失敗しました',
      );
    }
  };

  const handleConfirmRemoveCategory = async () => {
    if (!categoryToDelete) return;
    const { kind, id } = categoryToDelete;
    setCategoryToDelete(null);
    try {
      if (kind === 'expense') {
        await categoriesApi.removeExpenseCategory(id);
        if (expenseCategoryId === id) setExpenseCategoryId(null);
      } else {
        await categoriesApi.removeIncomeCategory(id);
        if (incomeCategoryId === id) setIncomeCategoryId(null);
      }
      await onCategoriesChanged();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'カテゴリの削除に失敗しました',
      );
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    if (assetId === null) {
      setError('資産を選択してください');
      return;
    }
    if (entryKind === 'transfer' && transferToAssetId === null) {
      setError('移動先資産を選択してください');
      return;
    }
    setSubmitting(true);
    try {
      await onSubmit({
        date,
        amount,
        entry_kind: entryKind,
        major_category_id: entryKind === 'expense' ? majorCategoryId : null,
        expense_category_id: entryKind === 'expense' ? expenseCategoryId : null,
        income_category_id: entryKind === 'income' ? incomeCategoryId : null,
        asset_id: assetId,
        transfer_to_asset_id:
          entryKind === 'transfer' ? transferToAssetId : null,
        memo: memo || null,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存に失敗しました');
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!onDelete) return;
    setShowDeleteConfirm(false);
    setSubmitting(true);
    try {
      await onDelete();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '削除に失敗しました');
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4">
      <div className="w-full max-w-[420px] rounded-md border border-line bg-paper p-5 shadow-lg">
        <h3 className="mb-3.5 text-[19px] font-semibold text-ink">
          {mode === 'create' ? '取引を追加' : '取引を編集'}
        </h3>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <div className="flex gap-3">
            <div className="flex flex-1 flex-col gap-1">
              <label className="font-mono text-[14.5px] tracking-wide text-ink-muted uppercase">
                日付
              </label>
              <input
                type="date"
                className="rounded border border-line bg-paper px-2.5 py-1.5 text-sm text-ink"
                value={date}
                onChange={(event) => setDate(event.target.value)}
                required
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-mono text-[14.5px] tracking-wide text-ink-muted uppercase">
                区分
              </label>
              <div className="flex overflow-hidden rounded border border-line">
                <button
                  type="button"
                  className={
                    entryKind === 'expense'
                      ? 'bg-expense-soft px-4 py-1.5 font-mono text-xs text-expense'
                      : 'px-4 py-1.5 font-mono text-xs text-ink-muted'
                  }
                  onClick={() => handleToggleKind('expense')}
                >
                  支出
                </button>
                <button
                  type="button"
                  className={
                    entryKind === 'income'
                      ? 'bg-income-soft px-4 py-1.5 font-mono text-xs text-income'
                      : 'px-4 py-1.5 font-mono text-xs text-ink-muted'
                  }
                  onClick={() => handleToggleKind('income')}
                >
                  収入
                </button>
                <button
                  type="button"
                  className={
                    entryKind === 'transfer'
                      ? 'bg-accent-soft px-4 py-1.5 font-mono text-xs text-accent'
                      : 'px-4 py-1.5 font-mono text-xs text-ink-muted'
                  }
                  onClick={() => handleToggleKind('transfer')}
                >
                  振替
                </button>
              </div>
            </div>
          </div>

          {entryKind === 'expense' && (
            <div className="flex flex-col gap-1">
              <label className="font-mono text-[14.5px] tracking-wide text-ink-muted uppercase">
                大カテゴリ
              </label>
              <div className="mb-1 flex flex-wrap gap-1.5">
                {majorCategories.map((major) => (
                  <button
                    key={major.id}
                    type="button"
                    className={
                      major.id === majorCategoryId
                        ? 'rounded border border-expense bg-expense-soft px-3 py-1 font-mono text-[15.5px] font-semibold text-expense'
                        : 'rounded border border-line-soft px-3 py-1 font-mono text-[15.5px] text-ink-muted'
                    }
                    onClick={() => handleSelectMajorCategory(major.id)}
                  >
                    {major.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {entryKind === 'transfer' ? (
            <div className="flex flex-col gap-1">
              <label className="font-mono text-[14.5px] tracking-wide text-ink-muted uppercase">
                移動先資産
              </label>
              <select
                className="rounded border border-line bg-paper px-2.5 py-1.5 text-sm text-ink"
                value={transferToAssetId ?? ''}
                onChange={(event) =>
                  setTransferToAssetId(Number(event.target.value))
                }
                required
              >
                <option value="" disabled>
                  選択してください
                </option>
                {assets
                  .filter((asset) => asset.id !== assetId)
                  .map((asset) => (
                    <option key={asset.id} value={asset.id}>
                      {asset.name}
                    </option>
                  ))}
              </select>
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              <label className="font-mono text-[14.5px] tracking-wide text-ink-muted uppercase">
                {entryKind === 'expense' ? '中カテゴリ' : '収入カテゴリ'}{' '}
                <span className="font-sans text-[15px] font-normal normal-case text-ink-muted">
                  (タップで選択・×で削除・+で新規追加)
                </span>
              </label>
              <div className="flex flex-wrap gap-1.5">
                {(entryKind === 'expense'
                  ? visibleExpenseCategories
                  : incomeCategories
                ).map((category) => {
                  const selected =
                    entryKind === 'expense'
                      ? category.id === expenseCategoryId
                      : category.id === incomeCategoryId;
                  return (
                    <span
                      key={category.id}
                      className={
                        selected
                          ? 'inline-flex cursor-pointer items-center gap-1.5 rounded-full border border-accent bg-accent-soft py-1 pr-1.5 pl-3 font-semibold text-accent'
                          : 'inline-flex cursor-pointer items-center gap-1.5 rounded-full border border-line-soft py-1 pr-1.5 pl-3 text-ink'
                      }
                      onClick={() =>
                        entryKind === 'expense'
                          ? setExpenseCategoryId(category.id)
                          : setIncomeCategoryId(category.id)
                      }
                    >
                      {category.name}
                      {!selected && (
                        <button
                          type="button"
                          className="font-mono text-[14px] text-ink-muted"
                          onClick={(event) => {
                            event.stopPropagation();
                            setCategoryToDelete({
                              kind:
                                entryKind === 'expense' ? 'expense' : 'income',
                              id: category.id,
                              name: category.name,
                            });
                          }}
                        >
                          ×
                        </button>
                      )}
                    </span>
                  );
                })}
                {addingCategory ? (
                  <span className="inline-flex items-center gap-1 rounded-full border border-dashed border-line py-1 pr-1.5 pl-3">
                    <input
                      autoFocus
                      className="w-24 border-none bg-transparent text-sm text-ink outline-none"
                      value={newCategoryName}
                      onChange={(event) =>
                        setNewCategoryName(event.target.value)
                      }
                      onKeyDown={(event) => {
                        if (event.key === 'Enter') {
                          event.preventDefault();
                          void handleAddCategory();
                        }
                      }}
                      maxLength={50}
                    />
                    <button
                      type="button"
                      className="font-mono text-[15px] text-accent"
                      onClick={() => void handleAddCategory()}
                    >
                      追加
                    </button>
                  </span>
                ) : (
                  <button
                    type="button"
                    className="rounded-full border border-dashed border-line px-3 py-1 font-mono text-[15.5px] text-ink-muted"
                    onClick={() => setAddingCategory(true)}
                  >
                    + 新規カテゴリ
                  </button>
                )}
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <div className="flex flex-1 flex-col gap-1">
              <label className="font-mono text-[14.5px] tracking-wide text-ink-muted uppercase">
                資産
              </label>
              <select
                className="rounded border border-line bg-paper px-2.5 py-1.5 text-sm text-ink"
                value={assetId ?? ''}
                onChange={(event) => setAssetId(Number(event.target.value))}
                required
              >
                {assets.map((asset) => (
                  <option key={asset.id} value={asset.id}>
                    {asset.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-1 flex-col gap-1">
              <label className="font-mono text-[14.5px] tracking-wide text-ink-muted uppercase">
                金額
              </label>
              <input
                type="number"
                className="rounded border border-line bg-paper px-2.5 py-1.5 text-sm text-ink"
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
                min="1"
                required
              />
            </div>
          </div>

          <div className="flex flex-col gap-1">
            <label className="font-mono text-[14.5px] tracking-wide text-ink-muted uppercase">
              メモ
            </label>
            <input
              className="rounded border border-line bg-paper px-2.5 py-1.5 text-sm text-ink"
              value={memo}
              onChange={(event) => setMemo(event.target.value)}
              maxLength={255}
            />
          </div>

          {error && <p className="text-xs text-expense">{error}</p>}

          <div className="mt-1 flex items-center justify-between">
            <div>
              {mode === 'edit' && (
                <button
                  type="button"
                  className="rounded border border-expense bg-expense-soft px-3 py-1.5 font-mono text-[15.5px] text-expense"
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={submitting}
                >
                  削除
                </button>
              )}
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                className="rounded border border-line bg-paper px-3 py-1.5 font-mono text-[15.5px] text-ink"
                onClick={onClose}
                disabled={submitting}
              >
                キャンセル
              </button>
              <button
                type="submit"
                className="rounded border border-accent bg-accent px-3 py-1.5 font-mono text-[15.5px] text-paper disabled:opacity-50"
                disabled={submitting}
              >
                {submitting ? '送信中...' : '保存'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {categoryToDelete && (
        <ConfirmDialog
          message={`「${categoryToDelete.name}」を削除しますか？`}
          onCancel={() => setCategoryToDelete(null)}
          onConfirm={() => void handleConfirmRemoveCategory()}
        />
      )}

      {showDeleteConfirm && (
        <ConfirmDialog
          message="この取引を削除しますか？"
          onCancel={() => setShowDeleteConfirm(false)}
          onConfirm={() => void handleConfirmDelete()}
        />
      )}
    </div>
  );
}
