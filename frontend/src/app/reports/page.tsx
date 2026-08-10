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
        <div className="flex items-baseline gap-2.5">
          <h2 className="text-[17px] text-ink">レポート</h2>
          <span className="rounded bg-tag-bg px-1.5 py-0.5 font-mono text-[11px] text-ink-muted">
            /reports
          </span>
        </div>

        {error && <p className="text-xs text-expense">{error}</p>}

        <div className="rounded border border-line-soft p-4">
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

          {!loading && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {monthsToShow.map((m, i) => {
                const breakdown = breakdowns[i];
                const isCenter = i === 1;
                const pieData = (breakdown?.items ?? []).map((item) => ({
                  name: item.major_category_name,
                  value: Number(item.amount),
                }));
                const total = breakdown ? Number(breakdown.total) : 0;

                return (
                  <div
                    key={`${m.year}-${m.month}`}
                    className={
                      isCenter
                        ? 'rounded border border-accent p-3'
                        : 'rounded border border-line-soft p-3'
                    }
                  >
                    <div
                      className={
                        isCenter
                          ? 'mb-2 text-center text-[12.5px] font-semibold text-accent'
                          : 'mb-2 text-center text-[12.5px] text-ink-muted'
                      }
                    >
                      {m.year}年{m.month}月
                    </div>
                    {breakdown && (
                      <>
                        <div className="mx-auto h-[140px] w-[140px]">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={pieData}
                                dataKey="value"
                                nameKey="name"
                                innerRadius={38}
                                outerRadius={65}
                                paddingAngle={pieData.length > 1 ? 2 : 0}
                              >
                                {pieData.map((entry, index) => (
                                  <Cell
                                    key={entry.name}
                                    fill={
                                      CATEGORY_COLORS[
                                        index % CATEGORY_COLORS.length
                                      ]
                                    }
                                  />
                                ))}
                              </Pie>
                              <Tooltip
                                formatter={(value) => formatYen(Number(value))}
                              />
                            </PieChart>
                          </ResponsiveContainer>
                        </div>
                        <div className="mt-2 flex flex-col gap-1 text-[11.5px]">
                          {breakdown.items.map((item, index) => (
                            <div
                              key={item.major_category_id}
                              className="flex items-center gap-1.5"
                            >
                              <span
                                className="h-2 w-2 flex-shrink-0 rounded-full"
                                style={{
                                  backgroundColor:
                                    CATEGORY_COLORS[
                                      index % CATEGORY_COLORS.length
                                    ],
                                }}
                              />
                              <span className="truncate text-ink">
                                {item.major_category_name}
                              </span>
                              <span className="ml-auto font-mono text-ink-muted tabular-nums">
                                {formatYen(item.amount)}
                                {total > 0
                                  ? ` (${Math.round((Number(item.amount) / total) * 100)}%)`
                                  : ''}
                              </span>
                            </div>
                          ))}
                          {breakdown.items.length === 0 && (
                            <p className="text-center text-ink-muted">
                              支出データなし
                            </p>
                          )}
                          <div className="mt-1 flex items-center gap-1.5 border-t border-line-soft pt-1 font-semibold">
                            <span className="text-ink">合計</span>
                            <span className="ml-auto font-mono text-ink tabular-nums">
                              {formatYen(breakdown.total)}
                            </span>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
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
