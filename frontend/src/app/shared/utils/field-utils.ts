export function asStringArray(val: unknown): string[] {
  if (!Array.isArray(val)) return [];
  return val.map(String);
}

/** Agrupa selecciones repetidas: "Ingeniero" x2 → { label: 'Ingeniero', count: 2 } */
export function groupSelections(val: unknown): { label: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const item of asStringArray(val)) {
    counts.set(item, (counts.get(item) ?? 0) + 1);
  }
  return Array.from(counts.entries()).map(([label, count]) => ({ label, count }));
}

/** Texto para exportación / vista previa documento */
export function formatListDisplay(val: unknown): string {
  const groups = groupSelections(val);
  if (!groups.length) return '';
  return groups.map(({ label, count }) => `${label} (${count})`).join(', ');
}

export function formatFieldDisplay(val: unknown): string {
  if (val === null || val === undefined || val === '' || (Array.isArray(val) && val.length === 0)) return 'N/A';
  if (Array.isArray(val)) return formatListDisplay(val) || 'N/A';
  return String(val);
}
