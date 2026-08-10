'use client';

import { useCallback, useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { ApiError } from '@/lib/api';
import { assetsApi } from '@/lib/assets';
import { AssetAdjustModal } from '@/components/AssetAdjustModal';
import { ASSET_TYPE_LABELS, AssetFormModal } from '@/components/AssetFormModal';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import type { Asset, AssetList, AssetType } from '@/types/asset';

const ASSET_ICON_LABELS: Record<AssetType, string> = {
  bank: '銀',
  cash: '¥',
  credit_card: 'card',
};

export default function AssetsPage() {
  const [data, setData] = useState<AssetList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formModal, setFormModal] = useState<{
    mode: 'create' | 'edit';
    asset?: Asset;
  } | null>(null);
  const [adjustTarget, setAdjustTarget] = useState<Asset | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Asset | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const loadAssets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await assetsApi.list();
      setData(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : '資産一覧の取得に失敗しました',
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- 初回マウント時のデータ取得
    void loadAssets();
  }, [loadAssets]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleteError(null);
    try {
      await assetsApi.remove(deleteTarget.id);
      setDeleteTarget(null);
      await loadAssets();
    } catch (err) {
      setDeleteError(
        err instanceof ApiError
          ? err.message
          : '削除に失敗しました。もう一度お試しください',
      );
    }
  };

  return (
    <AppShell>
      <div className="mb-1 flex items-baseline gap-2.5">
        <h2 className="text-[21px] text-ink">資産一覧</h2>
        <span className="rounded bg-tag-bg px-1.5 py-0.5 font-mono text-[15px] text-ink-muted">
          /assets
        </span>
      </div>
      <p className="mb-4.5 max-w-[70ch] text-[16.5px] text-ink-muted">
        登録済み資産(銀行口座・現金・カード)と残高、合計資産額を表示。「残高調整」から実際の残高を入力すると差額が調整取引として自動登録される。
      </p>

      {loading && <p className="text-xs text-ink-muted">読み込み中...</p>}
      {error && <p className="text-xs text-expense">{error}</p>}

      {data && (
        <>
          <div className="mb-4.5 flex gap-2.5">
            <div className="flex-none basis-[240px] rounded border border-line-soft bg-paper px-3.5 py-2.5">
              <div className="font-mono text-[14.5px] tracking-wide text-ink-muted uppercase">
                合計資産額
              </div>
              <div className="mt-0.5 font-mono text-lg text-ink tabular-nums">
                ¥{Number(data.total_balance).toLocaleString()}
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-2.5">
            {data.items.map((asset) => (
              <div
                key={asset.id}
                className="flex items-center gap-3 rounded border border-line-soft p-3.5"
              >
                <div className="flex h-[34px] w-[34px] flex-shrink-0 items-center justify-center rounded-full bg-accent-soft font-mono text-xs text-accent">
                  {ASSET_ICON_LABELS[asset.type]}
                </div>
                <div>
                  <div className="text-[17.5px] font-semibold text-ink">
                    {asset.name}
                  </div>
                  <div className="text-[15px] text-ink-muted">
                    {ASSET_TYPE_LABELS[asset.type]}
                  </div>
                </div>
                <div className="ml-auto font-mono text-[19px] text-ink tabular-nums">
                  ¥{Number(asset.balance).toLocaleString()}
                </div>
                <button
                  type="button"
                  className="ml-3.5 rounded border border-line bg-paper px-3 py-1.5 font-mono text-[15.5px] text-ink"
                  onClick={() => setAdjustTarget(asset)}
                >
                  残高調整
                </button>
                <button
                  type="button"
                  className="rounded border border-line bg-paper px-3 py-1.5 font-mono text-[15.5px] text-ink"
                  onClick={() => setFormModal({ mode: 'edit', asset })}
                >
                  編集
                </button>
                <button
                  type="button"
                  className="rounded border border-expense bg-expense-soft px-3 py-1.5 font-mono text-[15.5px] text-expense"
                  onClick={() => {
                    setDeleteError(null);
                    setDeleteTarget(asset);
                  }}
                >
                  削除
                </button>
              </div>
            ))}
            {data.items.length === 0 && (
              <p className="text-xs text-ink-muted">資産が登録されていません</p>
            )}
          </div>

          <div className="mt-4">
            <button
              type="button"
              className="rounded border border-accent bg-accent px-3 py-1.5 font-mono text-[15.5px] text-paper"
              onClick={() => setFormModal({ mode: 'create' })}
            >
              + 資産を追加
            </button>
          </div>
        </>
      )}

      {formModal && (
        <AssetFormModal
          mode={formModal.mode}
          initialAsset={formModal.asset}
          onClose={() => setFormModal(null)}
          onSubmit={async (values) => {
            if (formModal.mode === 'create') {
              await assetsApi.create(values);
            } else if (formModal.asset) {
              await assetsApi.update(formModal.asset.id, values);
            }
            await loadAssets();
          }}
        />
      )}

      {adjustTarget && (
        <AssetAdjustModal
          asset={adjustTarget}
          onClose={() => {
            setAdjustTarget(null);
            void loadAssets();
          }}
          onSubmit={(actualBalance) =>
            assetsApi.adjust(adjustTarget.id, actualBalance)
          }
        />
      )}

      {deleteTarget && (
        <div>
          <ConfirmDialog
            message={`「${deleteTarget.name}」を削除しますか？`}
            onCancel={() => setDeleteTarget(null)}
            onConfirm={handleDelete}
          />
          {deleteError && (
            <p className="fixed bottom-4 left-1/2 z-50 -translate-x-1/2 rounded bg-expense px-4 py-2 text-sm text-paper">
              {deleteError}
            </p>
          )}
        </div>
      )}
    </AppShell>
  );
}
