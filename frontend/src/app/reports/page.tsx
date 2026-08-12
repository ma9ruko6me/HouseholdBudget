'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { AppShell } from '@/components/AppShell';
import { CategoryDonutCard } from '@/components/CategoryDonutCard';
import { formatYen } from '@/lib/format';
import { reportsApi } from '@/lib/reports';
import type {
  AssetTrendPeriod,
  AssetTrendResponse,
  CategoryBreakdownResponse,
} from '@/types/report';

const TREND_PERIODS: { value: AssetTrendPeriod; label: string }[] = [
  { value: '3m', label: '3ヶ月' },
  { value: '6m', label: '6ヶ月' },
  { value: '1y', label: '1年' },
  { value: 'all', label: '全期間' },
];

type MonthKey = { year: number; month: number };

function shiftMonth({ year, month }: MonthKey, delta: number): MonthKey {
  let y = year;
  let m = month + delta;
  while (m < 1) {
    m += 12;
    y -= 1;
  }
  while (m > 12) {
    m -= 12;
    y += 1;
  }
  return { year: y, month: m };
}

function formatMonthDay(value: string): string {
  const [, month, day] = value.split('-');
  return `${month}/${day}`;
}

export default function ReportsPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [trendPeriod, setTrendPeriod] = useState<AssetTrendPeriod>('6m');

  const [breakdowns, setBreakdowns] = useState<
    (CategoryBreakdownResponse | null)[]
  >([null, null, null]);
  const [trend, setTrend] = useState<AssetTrendResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const monthsToShow = useMemo<MonthKey[]>(() => {
    const current = { year, month };
    return [shiftMonth(current, -1), current, shiftMonth(current, 1)];
  }, [year, month]);

  const loadBreakdown = useCallback(async () => {
    try {
      const results = await Promise.all(
        monthsToShow.map((m) => reportsApi.categoryBreakdown(m.year, m.month)),
      );
      setBreakdowns(results);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'カテゴリ別支出の取得に失敗しました',
      );
    }
  }, [monthsToShow]);

  const loadTrend = useCallback(async () => {
    try {
      const result = await reportsApi.assetTrend(trendPeriod);
      setTrend(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : '資産推移の取得に失敗しました',
      );
    }
  }, [trendPeriod]);

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

  const trendData = useMemo(
    () =>
      (trend?.items ?? []).map((point) => ({
        date: point.date,
        total_balance: Number(point.total_balance),
      })),
    [trend],
  );

  return (
    <AppShell>
      <div className="flex flex-col gap-4">
        <h2 className="-mx-5 -mt-5 bg-accent px-5 py-3.5 font-mono text-[21px] tracking-wide text-paper">
          REPORTS
        </h2>

        {error && <p className="text-xs text-expense">{error}</p>}

        <div className="rounded border border-line-soft p-4">
          <div className="mb-3 flex items-center justify-between">
            <div className="text-[17.5px] font-semibold text-ink">
              カテゴリ別支出
            </div>
            <div className="flex items-center gap-2.5 font-mono text-[16.5px]">
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

          {!loading && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {monthsToShow.map((m, i) => (
                <CategoryDonutCard
                  key={`${m.year}-${m.month}`}
                  label={`${m.year}年${m.month}月`}
                  highlighted={i === 1}
                  breakdown={breakdowns[i]}
                />
              ))}
            </div>
          )}
        </div>

        <div className="rounded border border-line-soft p-4">
          <div className="mb-3 flex items-center justify-between">
            <div className="text-[17.5px] font-semibold text-ink">資産推移</div>
            <div className="flex gap-1.5 font-mono text-[15.5px]">
              {TREND_PERIODS.map((p) => (
                <button
                  key={p.value}
                  type="button"
                  className={
                    p.value === trendPeriod
                      ? 'rounded border border-accent bg-accent px-2.5 py-1 text-paper'
                      : 'rounded border border-line px-2.5 py-1 text-ink-muted'
                  }
                  onClick={() => setTrendPeriod(p.value)}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {trend && (
            <div className="h-[260px] w-full">
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
                    formatter={(value) => [
                      formatYen(Number(value)),
                      '合計資産',
                    ]}
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
      </div>
    </AppShell>
  );
}
