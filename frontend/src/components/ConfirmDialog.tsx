'use client';

type Props = {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmDialog({ message, onConfirm, onCancel }: Props) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4">
      <div className="w-full max-w-[420px] rounded-md border border-line bg-paper p-5 shadow-lg">
        <p className="mb-5 text-sm text-ink">{message}</p>
        <div className="flex justify-end gap-2">
          <button
            type="button"
            className="rounded border border-line bg-paper px-3 py-1.5 font-mono text-[15.5px] text-ink"
            onClick={onCancel}
          >
            キャンセル
          </button>
          <button
            type="button"
            className="rounded border border-expense bg-expense-soft px-3 py-1.5 font-mono text-[15.5px] text-expense"
            onClick={onConfirm}
          >
            削除する
          </button>
        </div>
      </div>
    </div>
  );
}
