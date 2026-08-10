export function formatYen(value: string | number): string {
  return `¥${Number(value).toLocaleString()}`;
}
