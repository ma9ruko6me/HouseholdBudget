export type CategoryBreakdownItem = {
  major_category_id: number;
  major_category_name: string;
  amount: string;
};

export type CategoryBreakdownResponse = {
  year: number;
  month: number;
  items: CategoryBreakdownItem[];
  total: string;
};

export type AssetTrendPoint = {
  date: string;
  total_balance: string;
};

export type AssetTrendResponse = {
  items: AssetTrendPoint[];
};

export type AssetTrendPeriod = '3m' | '6m' | '1y' | 'all';
