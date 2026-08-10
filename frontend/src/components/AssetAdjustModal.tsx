'use client';

import { useState, type FormEvent } from 'react';
import type { Asset, AssetAdjustResult } from '@/types/asset';

type Props = {
  asset: Asset;
  onSubmit: (actualBalance: string) => Promise<AssetAdjustResult>;
  onClose: () => void;
};

export function AssetAdjustModal({ asset, onSubmit, onClose }: Props) {
  const [actualBalance, setActualBalance] = useState(asset.balance);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AssetAdjustResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const adjustResult = await onSubmit(actualBalance);
      setResult(adjustResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : '調整に失敗しました');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4">
      <div className="w-full max-w-[420px] rounded-md border border-line bg-paper p-5 shadow-lg">
        <h3 className="mb-3.5 text-[15px] font-semibold text-ink">
          残高調整: {asset.name}
        </h3>

        {result ? (
          <div className="flex flex-col gap-4">
            {result.transaction ? (
              <p className="text-sm text-ink">
                差額 {Number(result.transaction.amount).toLocaleString()} 円の
                {result.transaction.entry_kind === 'income' ? '入金' : '出金'}
                として調整取引を登録しました。
              </p>
            ) : (
              <p className="text-sm text-ink">
                現在の残高と差がないため、調整は行われませんでした。
              </p>
            )}
            <div className="flex justify-end">
              <button
                type="button"
                className="rounded border border-accent bg-accent px-3 py-1.5 font-mono text-[11.5px] text-paper"
                onClick={onClose}
              >
                閉じる
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <p className="font-mono text-xs text-ink-muted">
              現在の残高: {Number(asset.balance).toLocaleString()} 円
            </p>
            <div className="flex flex-col gap-1">
              <label
                className="font-mono text-[10.5px] tracking-wide text-ink-muted uppercase"
                htmlFor="actual-balance"
              >
                実際の残高
              </label>
              <input
                id="actual-balance"
                type="number"
                className="rounded border border-line bg-paper px-2.5 py-1.5 text-sm text-ink"
                value={actualBalance}
                onChange={(event) => setActualBalance(event.target.value)}
                required
              />
            </div>
            {error && <p className="text-xs text-expense">{error}</p>}
            <div className="mt-1 flex justify-end gap-2">
              <button
                type="button"
                className="rounded border border-line bg-paper px-3 py-1.5 font-mono text-[11.5px] text-ink"
                onClick={onClose}
                disabled={submitting}
              >
                キャンセル
              </button>
              <button
                type="submit"
                className="rounded border border-accent bg-accent px-3 py-1.5 font-mono text-[11.5px] text-paper disabled:opacity-50"
                disabled={submitting}
              >
                {submitting ? '送信中...' : '調整する'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
