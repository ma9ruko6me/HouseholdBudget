import type { EntryKind } from '@/types/transaction';

export type RecurringTransaction = {
  id: number;
  amount: string;
  entry_kind: EntryKind;
  major_category_id: number | null;
  expense_category_id: number | null;
  income_category_id: number | null;
  asset_id: number;
  day_of_month: number;
  last_generated_date: string | null;
  memo: string | null;
};

export type RecurringTransactionList = {
  items: RecurringTransaction[];
};

export type RecurringTransactionInput = {
  amount: string;
  entry_kind: EntryKind;
  major_category_id: number | null;
  expense_category_id: number | null;
  income_category_id: number | null;
  asset_id: number;
  day_of_month: number;
  memo: string | null;
};
