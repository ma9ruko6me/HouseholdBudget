import { api } from '@/lib/api';
import type {
  RecurringTransaction,
  RecurringTransactionInput,
  RecurringTransactionList,
} from '@/types/recurringTransaction';

export const recurringTransactionsApi = {
  list: () => api.get<RecurringTransactionList>('/recurring-transactions'),
  create: (input: RecurringTransactionInput) =>
    api.post<RecurringTransaction>('/recurring-transactions', input),
  update: (id: number, input: RecurringTransactionInput) =>
    api.put<RecurringTransaction>(`/recurring-transactions/${id}`, input),
  remove: (id: number) => api.delete<void>(`/recurring-transactions/${id}`),
};
