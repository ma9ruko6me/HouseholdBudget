export type EntryKind = 'income' | 'expense' | 'transfer';
export type EntryType = 'normal' | 'adjustment';

export type Transaction = {
  id: number;
  date: string;
  amount: string;
  entry_kind: EntryKind;
  entry_type: EntryType;
  major_category_id: number | null;
  expense_category_id: number | null;
  income_category_id: number | null;
  asset_id: number;
  transfer_to_asset_id: number | null;
  memo: string | null;
};

export type TransactionList = {
  items: Transaction[];
};

export type TransactionInput = {
  date: string;
  amount: string;
  entry_kind: EntryKind;
  major_category_id: number | null;
  expense_category_id: number | null;
  income_category_id: number | null;
  asset_id: number;
  transfer_to_asset_id: number | null;
  memo: string | null;
};

export type MonthlySummary = {
  year: number;
  month: number;
  income_total: string;
  expense_total: string;
  balance: string;
};
