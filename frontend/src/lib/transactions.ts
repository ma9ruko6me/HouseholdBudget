import { api } from '@/lib/api';
import type {
  MonthlySummary,
  Transaction,
  TransactionInput,
  TransactionList,
} from '@/types/transaction';

export const transactionsApi = {
  list: (year: number, month: number) =>
    api.get<TransactionList>('/transactions', { year, month }),
  create: (input: TransactionInput) =>
    api.post<Transaction>('/transactions', input),
  update: (id: number, input: TransactionInput) =>
    api.put<Transaction>(`/transactions/${id}`, input),
  remove: (id: number) => api.delete<void>(`/transactions/${id}`),
  monthlySummary: (year: number, month: number) =>
    api.get<MonthlySummary>('/summary/monthly', { year, month }),
};
