import type { CardPrice } from "@/types/api";

type CardPricesProps = {
  prices: CardPrice[];
};

export function CardPrices({ prices }: CardPricesProps) {
  if (prices.length === 0) {
    return (
      <div className="bg-bg-secondary border border-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-text-secondary">Prices</h3>
        <p className="text-xs text-text-muted mt-2">No price data available</p>
      </div>
    );
  }

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <h3 className="text-sm font-medium text-text-secondary">Prices</h3>
      <div className="overflow-x-auto -mx-4 px-4">
      <table className="w-full text-xs min-w-[320px]">
        <thead>
          <tr className="text-text-muted border-b border-border">
            <th className="text-left pb-1.5 font-medium">Provider</th>
            <th className="text-left pb-1.5 font-medium">Finish</th>
            <th className="text-left pb-1.5 font-medium">Type</th>
            <th className="text-right pb-1.5 font-medium">Price</th>
          </tr>
        </thead>
        <tbody>
          {prices.map((p, i) => (
            <tr key={i} className="border-b border-border/50 last:border-none">
              <td className="py-1.5 text-text-secondary capitalize">{p.provider}</td>
              <td className="py-1.5 text-text-muted capitalize">{p.finish}</td>
              <td className="py-1.5 text-text-muted capitalize">{p.listing_type}</td>
              <td className="py-1.5 text-right text-success font-medium">${p.price.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  );
}
