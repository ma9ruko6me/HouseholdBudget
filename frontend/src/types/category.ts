export type MajorCategory = {
  id: number;
  name: string;
  sort_order: number;
};

export type ExpenseCategory = {
  id: number;
  major_category_id: number;
  name: string;
  sort_order: number;
};

export type IncomeCategory = {
  id: number;
  name: string;
  sort_order: number;
};
