import { useState, useRef, useEffect, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { useCard } from "@/api/hooks";
import { CardLargeView } from "@/components/CardLargeView/CardLargeView";

type CardHoverLargeProps = {
  uuid: string;
  pinned?: boolean;
  quantity?: number;
  onPin?: (uuid: string) => void;
  onAddToDeck?: (uuid: string) => void;
  onFindSimilar?: (uuid: string) => void;
  onClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
  children: ReactNode;
};

const DELAY_SHOW = 400;
const DELAY_HIDE = 150;

export function CardHoverLarge({
  uuid,
  pinned,
  quantity,
  onPin,
  onAddToDeck,
  onFindSimilar,
  onClick,
  onSetClick,
  children,
}: CardHoverLargeProps) {
  const [hovering, setHovering] = useState(false);
  const [visible, setVisible] = useState(false);
  const showTimer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const hideTimer = useRef<ReturnType<typeof setTimeout>>(undefined);

  const { data: card } = useCard(hovering ? uuid : "");

  function handleMouseEnter() {
    clearTimeout(hideTimer.current);
    setHovering(true);
    showTimer.current = setTimeout(() => {
      setVisible(true);
    }, DELAY_SHOW);
  }

  function handleMouseLeave() {
    clearTimeout(showTimer.current);
    hideTimer.current = setTimeout(() => {
      setVisible(false);
      setHovering(false);
    }, DELAY_HIDE);
  }

  function handlePreviewEnter() {
    clearTimeout(hideTimer.current);
  }

  function handlePreviewLeave() {
    hideTimer.current = setTimeout(() => {
      setVisible(false);
      setHovering(false);
    }, DELAY_HIDE);
  }

  useEffect(() => {
    return () => {
      clearTimeout(showTimer.current);
      clearTimeout(hideTimer.current);
    };
  }, []);

  return (
    <div
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}

      {visible && card && createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center pointer-events-none">
          <div
            className="pointer-events-auto max-h-[90vh] overflow-y-auto"
            onMouseEnter={handlePreviewEnter}
            onMouseLeave={handlePreviewLeave}
          >
            <CardLargeView
              card={card}
              pinned={pinned}
              quantity={quantity}
              onPin={onPin}
              onAddToDeck={onAddToDeck}
              onFindSimilar={onFindSimilar}
              onClick={onClick}
              onSetClick={onSetClick}
            />
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
