import { api } from '@/lib/api';
import type {
  ExpenseCategory,
  IncomeCategory,
  MajorCategory,
} from '@/types/category';

export const categoriesApi = {
  listMajorCategories: () => api.get<MajorCategory[]>('/major-categories'),
  listExpenseCategories: () =>
    api.get<ExpenseCategory[]>('/expense-categories'),
  createExpenseCategory: (majorCategoryId: number, name: string) =>
    api.post<ExpenseCategory>('/expense-categories', {
      major_category_id: majorCategoryId,
      name,
    }),
  removeExpenseCategory: (id: number) =>
    api.delete<void>(`/expense-categories/${id}`),
  listIncomeCategories: () => api.get<IncomeCategory[]>('/income-categories'),
  createIncomeCategory: (name: string) =>
    api.post<IncomeCategory>('/income-categories', { name }),
  removeIncomeCategory: (id: number) =>
    api.delete<void>(`/income-categories/${id}`),
};
