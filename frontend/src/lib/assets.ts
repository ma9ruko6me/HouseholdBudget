import { api } from '@/lib/api';
import type {
  Asset,
  AssetAdjustResult,
  AssetCreateInput,
  AssetList,
  AssetUpdateInput,
} from '@/types/asset';

export const assetsApi = {
  list: () => api.get<AssetList>('/assets'),
  create: (input: AssetCreateInput) => api.post<Asset>('/assets', input),
  update: (id: number, input: AssetUpdateInput) =>
    api.put<Asset>(`/assets/${id}`, input),
  remove: (id: number) => api.delete<void>(`/assets/${id}`),
  adjust: (id: number, actualBalance: string) =>
    api.post<AssetAdjustResult>(`/assets/${id}/adjust`, {
      actual_balance: actualBalance,
    }),
};
