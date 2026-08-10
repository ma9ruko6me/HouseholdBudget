'use client';

import { useState, type FormEvent } from 'react';
import type { Asset, AssetType } from '@/types/asset';

const ASSET_TYPE_LABELS: Record<AssetType, string> = {
  bank: '銀行口座',
  cash: '現金',
  credit_card: 'クレジットカード',
};

type AssetFormValues = {
  name: string;
  type: AssetType;
  balance: string;
};

type Props = {
  mode: 'create' | 'edit';
  initialAsset?: Asset;
  onSubmit: (values: AssetFormValues) => Promise<void>;
  onClose: () => void;
};

export function AssetFormModal({
  mode,
  initialAsset,
  onSubmit,
  onClose,
}: Props) {
  const [name, setName] = useState(initialAsset?.name ?? '');
  const [type, setType] = useState<AssetType>(initialAsset?.type ?? 'bank');
  const [balance, setBalance] = useState(initialAsset?.balance ?? '0');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit({ name, type, balance });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '登録に失敗しました');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4">
      <div className="w-full max-w-[420px] rounded-md border border-line bg-paper p-5 shadow-lg">
        <h3 className="mb-3.5 text-[15px] font-semibold text-ink">
          {mode === 'create' ? '資産の新規登録' : '資産の編集'}
        </h3>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <div className="flex flex-col gap-1">
            <label
              className="font-mono text-[10.5px] tracking-wide text-ink-muted uppercase"
              htmlFor="asset-name"
            >
              資産名
            </label>
            <input
              id="asset-name"
              className="rounded border border-line bg-paper px-2.5 py-1.5 text-sm text-ink"
              value={name}
              onChange={(event) => setName(event.target.value)}
              maxLength={50}
              required
            />
          </div>
          <div className="flex flex-col gap-1">
            <label
              className="font-mono text-[10.5px] tracking-wide text-ink-muted uppercase"
              htmlFor="asset-type"
            >
              種別
            </label>
            <select
              id="asset-type"
              className="rounded border border-line bg-paper px-2.5 py-1.5 text-sm text-ink"
              value={type}
              onChange={(event) => setType(event.target.value as AssetType)}
            >
              {Object.entries(ASSET_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
          {mode === 'create' && (
            <div className="flex flex-col gap-1">
              <label
                className="font-mono text-[10.5px] tracking-wide text-ink-muted uppercase"
                htmlFor="asset-balance"
              >
                初期残高
              </label>
              <input
                id="asset-balance"
                type="number"
                className="rounded border border-line bg-paper px-2.5 py-1.5 text-sm text-ink"
                value={balance}
                onChange={(event) => setBalance(event.target.value)}
                required
              />
            </div>
          )}
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
              {submitting ? '送信中...' : '保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export { ASSET_TYPE_LABELS };
