'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { AppShell } from '@/components/AppShell';
import { reportsApi } from '@/lib/reports';
import type {
  AssetTrendMonths,
  AssetTrendResponse,
  CategoryBreakdownResponse,
} from '@/types/report';

const CATEGORY_COLORS = [
  '#a3453b',
  '#c98a5b',
  '#3d5a80',
  '#7c9070',
  '#6b5b95',
  '#c9a227',
];

const TREND_PERIODS: AssetTrendMonths[] = [3, 6, 12];

function formatYen(value: string | number): string {
  return `¥${Number(value).toLocaleString()}`;
}

function formatMonthDay(value: string): string {
  const [, month, day] = value.split('-');
  return `${month}/${day}`;
}

export default function ReportsPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [trendMonths, setTrendMonths] = useState<AssetTrendMonths>(6);

  const [breakdown, setBreakdown] = useState<CategoryBreakdownResponse | null>(
    null,
  );
  const [trend, setTrend] = useState<AssetTrendResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadBreakdown = useCallback(async () => {
    try {
      const result = await reportsApi.categoryBreakdown(year, month);
      setBreakdown(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'カテゴリ別支出の取得に失敗しました',
      );
    }
  }, [year, month]);

  const loadTrend = useCallback(async () => {
    try {
      const result = await reportsApi.assetTrend(trendMonths);
      setTrend(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : '資産推移の取得に失敗しました',
      );
    }
  }, [trendMonths]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- 月切り替え時のデータ再取得
    setLoading(true);
    setError(null);
    void loadBreakdown().finally(() => setLoading(false));
  }, [loadBreakdown]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- 期間切り替え時のデータ再取得
    void loadTrend();
  }, [loadTrend]);

  const handlePrevMonth = () => {
    if (month === 1) {
      setYear((y) => y - 1);
      setMonth(12);
    } else {
      setMonth((m) => m - 1);
    }
  };

  const handleNextMonth = () => {
    if (month === 12) {
      setYear((y) => y + 1);
      setMonth(1);
    } else {
      setMonth((m) => m + 1);
    }
  };

  const pieData = useMemo(
    () =>
      (breakdown?.items ?? []).map((item) => ({
        name: item.major_category_name,
        value: Number(item.amount),
      })),
    [breakdown],
  );

  const trendData = useMemo(
    () =>
      (trend?.items ?? []).map((point) => ({
        date: point.date,
        total_balance: Number(point.total_balance),
      })),
    [trend],
  );

  const total = breakdown ? Number(breakdown.total) : 0;

  return (
    <AppShell>
      <div className="mb-1 flex items-baseline gap-2.5">
        <h2 className="text-[17px] text-ink">レポート</h2>
        <span className="rounded bg-tag-bg px-1.5 py-0.5 font-mono text-[11px] text-ink-muted">
          /reports
        </span>
      </div>

      {error && <p className="mb-2 text-xs text-expense">{error}</p>}

      <div className="mb-6 rounded border border-line-soft p-4">
        <div className="mb-3 flex items-center justify-between">
          <div className="text-[13.5px] font-semibold text-ink">
            カテゴリ別支出
          </div>
          <div className="flex items-center gap-2.5 font-mono text-[12.5px]">
            <button
              type="button"
              className="flex h-6 w-6 items-center justify-center rounded border border-line text-ink-muted"
              onClick={handlePrevMonth}
            >
              ‹
            </button>
            <div className="text-sm font-semibold text-ink">
              {year}年{month}月
            </div>
            <button
              type="button"
              className="flex h-6 w-6 items-center justify-center rounded border border-line text-ink-muted"
              onClick={handleNextMonth}
            >
              ›
            </button>
          </div>
        </div>

        {loading && <p className="text-xs text-ink-muted">読み込み中...</p>}

        {!loading && breakdown && (
          <div className="flex flex-wrap items-center gap-6">
            <div className="h-[200px] w-[200px] flex-shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={pieData.length > 1 ? 2 : 0}
                  >
                    {pieData.map((entry, index) => (
                      <Cell
                        key={entry.name}
                        fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatYen(Number(value))} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-col gap-1.5 text-[12.5px]">
              {breakdown.items.map((item, index) => (
                <div
                  key={item.major_category_id}
                  className="flex items-center gap-2"
                >
                  <span
                    className="h-2.5 w-2.5 flex-shrink-0 rounded-full"
                    style={{
                      backgroundColor:
                        CATEGORY_COLORS[index % CATEGORY_COLORS.length],
                    }}
                  />
                  <span className="text-ink">{item.major_category_name}</span>
                  <span className="ml-auto font-mono text-ink-muted tabular-nums">
                    {formatYen(item.amount)}
                    {total > 0
                      ? ` (${Math.round((Number(item.amount) / total) * 100)}%)`
                      : ''}
                  </span>
                </div>
              ))}
              {breakdown.items.length === 0 && (
                <p className="text-xs text-ink-muted">
                  この月の支出データはありません
                </p>
              )}
              <div className="mt-1.5 flex items-center gap-2 border-t border-line-soft pt-1.5 font-semibold">
                <span className="text-ink">支出合計</span>
                <span className="ml-auto font-mono text-ink tabular-nums">
                  {formatYen(breakdown.total)}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="rounded border border-line-soft p-4">
        <div className="mb-3 flex items-center justify-between">
          <div className="text-[13.5px] font-semibold text-ink">資産推移</div>
          <div className="flex gap-1.5 font-mono text-[11.5px]">
            {TREND_PERIODS.map((p) => (
              <button
                key={p}
                type="button"
                className={
                  p === trendMonths
                    ? 'rounded border border-accent bg-accent px-2.5 py-1 text-paper'
                    : 'rounded border border-line px-2.5 py-1 text-ink-muted'
                }
                onClick={() => setTrendMonths(p)}
              >
                {p === 12 ? '1年' : `${p}ヶ月`}
              </button>
            ))}
          </div>
        </div>

        {trend && (
          <div className="h-[220px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <XAxis
                  dataKey="date"
                  tickFormatter={formatMonthDay}
                  stroke="var(--color-ink-muted)"
                  fontSize={11}
                />
                <YAxis
                  tickFormatter={(value: number) => formatYen(value)}
                  stroke="var(--color-ink-muted)"
                  fontSize={11}
                  width={90}
                />
                <Tooltip
                  labelFormatter={(label) => label}
                  formatter={(value) => [formatYen(Number(value)), '合計資産']}
                />
                <Line
                  type="monotone"
                  dataKey="total_balance"
                  stroke="var(--color-accent)"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </AppShell>
  );
}
