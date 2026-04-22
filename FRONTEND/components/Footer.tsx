import { SITE } from '@/src/lib/content';

export default function Footer() {
  const { privacy, clinical } = SITE.footer;

  return (
    <footer className="border-t border-slate-700 mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <p className="text-slate-500 text-sm text-center">{privacy}</p>
        <p className="text-slate-600 text-xs text-center mt-1">{clinical}</p>
      </div>
    </footer>
  );
}
