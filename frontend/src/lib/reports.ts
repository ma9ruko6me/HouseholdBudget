import { api } from '@/lib/api';
import type {
  AssetTrendMonths,
  AssetTrendResponse,
  CategoryBreakdownResponse,
} from '@/types/report';

export const reportsApi = {
  categoryBreakdown: (year: number, month: number) =>
    api.get<CategoryBreakdownResponse>('/reports/category-breakdown', {
      year,
      month,
    }),
  assetTrend: (months: AssetTrendMonths) =>
    api.get<AssetTrendResponse>('/reports/asset-trend', { months }),
};
