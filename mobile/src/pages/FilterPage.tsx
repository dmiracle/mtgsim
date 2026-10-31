import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCardCount, useCreateTierList, useSets, useTierLists, useUserTags } from "../api";
import { FilterForm } from "../components/FilterForm";
import { DEFAULT_FILTERS, LAST_REVIEW_KEY, listParam, loadFilters, saveFilters, setParam } from "../filters";

export function FilterPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState(loadFilters);
  const [setQuery, setSetQuery] = useState("");
  const sets = useSets(setQuery);
  const userTags = useUserTags();
  const tierLists = useTierLists();
  const count = useCardCount(filters);
  const createTierList = useCreateTierList();
  const selectedSets = listParam(filters, "sets");

  const createGradeList = async (name: string) => {
    const list = await createTierList.mutateAsync({
      name,
      set_code: selectedSets.length === 1 ? selectedSets[0] : undefined,
    });
    setFilters((f) => {
      const next = setParam(f, "grade_list", String(list.id));
      return f.not_in_tier_list ? setParam(next, "not_in_tier_list", String(list.id)) : next;
    });
  };
  const lastReview = localStorage.getItem(LAST_REVIEW_KEY);

  useEffect(() => saveFilters(filters), [filters]);

  return (
    <>
      {lastReview && (
        <button
          onClick={() => navigate(`/review?${lastReview}`)}
          className="mx-4 mt-[max(1rem,env(safe-area-inset-top))] block w-[calc(100%-2rem)] rounded-xl border border-accent px-4 py-3 text-left text-accent"
        >
          Resume last review ›
        </button>
      )}
      <FilterForm
        filters={filters}
        onChange={setFilters}
        sets={sets.data?.data ?? []}
        setQuery={setQuery}
        onSetQueryChange={setSetQuery}
        userTags={userTags.data?.data ?? []}
        tierLists={tierLists.data?.data ?? []}
        count={count.data}
        onStart={() => navigate(`/review?${new URLSearchParams({ ...filters, i: "0" })}`)}
        onReset={() => setFilters(DEFAULT_FILTERS)}
        onCreateGradeList={createGradeList}
      />
    </>
  );
}
