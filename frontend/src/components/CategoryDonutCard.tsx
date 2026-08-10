import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { formatYen } from '@/lib/format';
import type { CategoryBreakdownResponse } from '@/types/report';

export const CATEGORY_COLORS = [
  '#a3453b',
  '#c98a5b',
  '#3d5a80',
  '#7c9070',
  '#6b5b95',
  '#c9a227',
];

type Props = {
  label: string;
  highlighted?: boolean;
  breakdown: CategoryBreakdownResponse | null;
};

export function CategoryDonutCard({ label, highlighted, breakdown }: Props) {
  const pieData = (breakdown?.items ?? []).map((item) => ({
    name: item.major_category_name,
    value: Number(item.amount),
  }));
  const total = breakdown ? Number(breakdown.total) : 0;

  return (
    <div
      className={
        highlighted
          ? 'rounded border border-accent p-3'
          : 'rounded border border-line-soft p-3'
      }
    >
      <div
        className={
          highlighted
            ? 'mb-2 text-center text-[16.5px] font-semibold text-accent'
            : 'mb-2 text-center text-[16.5px] text-ink-muted'
        }
      >
        {label}
      </div>
      {breakdown && (
        <>
          <div className="mx-auto aspect-square w-full max-w-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius="55%"
                  outerRadius="90%"
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
          <div className="mt-2 flex flex-col gap-1 text-[15.5px]">
            {breakdown.items.map((item, index) => (
              <div
                key={item.major_category_id}
                className="flex items-center gap-1.5"
              >
                <span
                  className="h-2 w-2 flex-shrink-0 rounded-full"
                  style={{
                    backgroundColor:
                      CATEGORY_COLORS[index % CATEGORY_COLORS.length],
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
              <p className="text-center text-ink-muted">支出データなし</p>
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
}
