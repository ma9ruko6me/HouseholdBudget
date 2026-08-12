import { api } from '@/lib/api';
import type {
  AssetTrendPeriod,
  AssetTrendResponse,
  CategoryBreakdownResponse,
} from '@/types/report';

export const reportsApi = {
  categoryBreakdown: (year: number, month: number) =>
    api.get<CategoryBreakdownResponse>('/reports/category-breakdown', {
      year,
      month,
    }),
  assetTrend: (period: AssetTrendPeriod) =>
    api.get<AssetTrendResponse>('/reports/asset-trend', { period }),
};
