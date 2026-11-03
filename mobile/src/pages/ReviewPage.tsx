import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  PAGE_SIZE,
  cardPageQuery,
  useCardPage,
  useEvaluationSet,
  useSetEvaluation,
  useSetGrade,
  useTierList,
} from "../api";
import { ReviewScreen } from "../components/ReviewScreen";
import { LAST_REVIEW_KEY, summarizeFilters, type Filters } from "../filters";
import type { Scores, Situation } from "../types";

const UNRATED: Scores = { developing: null, parity: null, behind: null, ahead: null };

const IMAGE_LOOKAHEAD = 3;

export function ReviewPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [params, setParams] = useSearchParams();
  const index = Number(params.get("i") ?? 0);
  const filters: Filters = Object.fromEntries([...params].filter(([k]) => k !== "i"));
  const page = Math.floor(index / PAGE_SIZE) + 1;
  const { data } = useCardPage(filters, page);
  const total = data?.pagination.total ?? 0;
  const cards = data?.pagination.page === page ? data.data : [];
  const offset = index % PAGE_SIZE;
  const card = cards[offset];
  const gradeList = useTierList(filters.grade_list);
  const setGrade = useSetGrade(filters.grade_list);
  const grades = new Map(gradeList.data?.entries.map((e) => [e.card_name, e.tier]));
  const evalSet = useEvaluationSet(filters.eval_set);
  const setEvaluation = useSetEvaluation(filters.eval_set);
  const evaluation = evalSet.data?.entries.find((e) => e.card_name === card?.name);
  const scores: Scores = evaluation
    ? { developing: evaluation.developing, parity: evaluation.parity, behind: evaluation.behind, ahead: evaluation.ahead }
    : UNRATED;
  const rate = (situation: Situation, stars: number | null) =>
    setEvaluation.mutate({ cardName: card!.name, scores: { ...scores, [situation]: stars } });

  const seek = (i: number) => setParams({ ...filters, i: String(i) }, { replace: true });

  // Grading a card advances to the next one; clearing a grade stays put. With
  // "ungraded only" the graded card drops out of the results, so the next card
  // slides into the current position instead.
  const grade = (tier: string | null) => {
    if (filters.not_in_tier_list) {
      setGrade.mutate(
        { cardName: card!.name, tier },
        { onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cards"] }) },
      );
      return;
    }
    setGrade.mutate({ cardName: card!.name, tier });
    if (tier && index < total - 1) seek(index + 1);
  };

  useEffect(() => localStorage.setItem(LAST_REVIEW_KEY, params.toString()), [params]);

  // Warm the next page and the next few card images so swiping feels instant.
  useEffect(() => {
    if (offset >= PAGE_SIZE - 10 && page < (data?.pagination.pages ?? 0)) {
      queryClient.prefetchQuery(cardPageQuery(filters, page + 1));
    }
    for (const c of cards.slice(offset + 1, offset + 1 + IMAGE_LOOKAHEAD)) {
      if (c.image_url) new Image().src = c.image_url;
    }
  }, [index, cards]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" && index < total - 1) seek(index + 1);
      if (e.key === "ArrowLeft" && index > 0) seek(index - 1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  useEffect(() => window.scrollTo(0, 0), [index]);

  // Results can shrink under us (ungraded-only grading), so clamp the position.
  useEffect(() => {
    if (total > 0 && index >= total) seek(total - 1);
  }, [index, total]);

  return (
    <ReviewScreen
      card={card}
      index={index}
      total={total}
      summary={summarizeFilters(filters)}
      onSeek={seek}
      onExit={() => navigate("/")}
      grading={
        gradeList.data
          ? { listName: gradeList.data.name, grade: grades.get(card?.name ?? ""), onGrade: grade }
          : undefined
      }
      evaluating={evalSet.data ? { setName: evalSet.data.name, scores, onRate: rate } : undefined}
    />
  );
}
