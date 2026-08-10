export type AssetType = 'bank' | 'cash' | 'credit_card';

export type Asset = {
  id: number;
  name: string;
  type: AssetType;
  balance: string;
  sort_order: number;
};

export type AssetList = {
  items: Asset[];
  total_balance: string;
};

export type AssetCreateInput = {
  name: string;
  type: AssetType;
  balance: string;
};

export type AssetUpdateInput = {
  name: string;
  type: AssetType;
};

export type AdjustmentTransaction = {
  id: number;
  date: string;
  amount: string;
  entry_kind: 'income' | 'expense';
  entry_type: 'normal' | 'adjustment';
  asset_id: number;
  memo: string | null;
};

export type AssetAdjustResult = {
  asset: Asset;
  transaction: AdjustmentTransaction | null;
};
