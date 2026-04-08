// Types
export type * from "./types/api";
export type * from "./types/flashcards";

// API client & hooks
export { apiFetch, buildParams } from "./api/client";
export * from "./api/hooks";
export * from "./api/flashcard-hooks";

// Context
export { ActiveDeckProvider, useActiveDeck } from "./context/ActiveDeckContext";

// Fixtures
export * from "./fixtures/index";

// Components — re-export each component directory
export { AddCardToDeckModal } from "./components/AddCardToDeckModal/AddCardToDeckModal";
export { AddToDeckModal } from "./components/AddToDeckModal/AddToDeckModal";
export { AppLayout } from "./components/AppLayout/AppLayout";
export { CardFilterBar } from "./components/CardFilterBar/CardFilterBar";
export type { CardFilters } from "./components/CardFilterBar/CardFilterBar";
export { CardGrid } from "./components/CardGrid/CardGrid";
export { CardGridItem } from "./components/CardGridItem/CardGridItem";
export { CardHoverLarge } from "./components/CardHoverLarge/CardHoverLarge";
export { CardIdentity } from "./components/CardIdentity/CardIdentity";
export { CardKeywords } from "./components/CardKeywords/CardKeywords";
export { CardLargeView } from "./components/CardLargeView/CardLargeView";
export { CardMetadata } from "./components/CardMetadata/CardMetadata";
export { CardOracleText } from "./components/CardOracleText/CardOracleText";
export { CardPrices } from "./components/CardPrices/CardPrices";
export { CardQuiz } from "./components/CardQuiz/CardQuiz";
export { CardRecallFlashcard } from "./components/CardRecallFlashcard/CardRecallFlashcard";
export { CardQuizGenerator } from "./components/CardQuizGenerator/CardQuizGenerator";
export { CardRawData } from "./components/CardRawData/CardRawData";
export { CardRecallChallenge } from "./components/CardRecallChallenge/CardRecallChallenge";
export { CardTable } from "./components/CardTable/CardTable";
export { CardTypeFilter } from "./components/CardTypeFilter/CardTypeFilter";
export { CardTypeIcon } from "./components/CardTypeIcon/CardTypeIcon";
export { CollectionStatus } from "./components/CollectionStatus/CollectionStatus";
export { ColorIdentityPicker } from "./components/ColorIdentityPicker/ColorIdentityPicker";
export { CopyUuidButton } from "./components/CopyUuidButton/CopyUuidButton";
export { DeckAppearances } from "./components/DeckAppearances/DeckAppearances";
export { DeckCardItem } from "./components/DeckCardItem/DeckCardItem";
export { DeckCardList } from "./components/DeckCardList/DeckCardList";
export { DeckCards } from "./components/DeckCards/DeckCards";
export { DeckCreateModal } from "./components/DeckCreateModal/DeckCreateModal";
export { DeckImportModal } from "./components/DeckImportModal/DeckImportModal";
export { DeckListItem } from "./components/DeckListItem/DeckListItem";
export { DeckStats } from "./components/DeckStats/DeckStats";
export { FlashcardCard } from "./components/FlashcardCard/FlashcardCard";
export { FlipCard } from "./components/FlipCard/FlipCard";
export { FormatLegalityBadges } from "./components/FormatLegalityBadges/FormatLegalityBadges";
export { GenerateDialog } from "./components/GenerateDialog/GenerateDialog";
export { GlossaryBrowser } from "./components/GlossaryBrowser/GlossaryBrowser";
export { KeywordBrowser } from "./components/KeywordBrowser/KeywordBrowser";
export { KeywordCloud } from "./components/KeywordCloud/KeywordCloud";
export { ManaSymbols } from "./components/ManaSymbols/ManaSymbols";
export { MtgaImportModal } from "./components/MtgaImportModal/MtgaImportModal";
export { OracleTagsDropdown } from "./components/OracleTagsDropdown/OracleTagsDropdown";
export { OtherPrintings } from "./components/OtherPrintings/OtherPrintings";
export { OwnershipToggle } from "./components/OwnershipToggle/OwnershipToggle";
export { PackConfigPanel } from "./components/PackConfigPanel/PackConfigPanel";
export { PackDisplay } from "./components/PackDisplay/PackDisplay";
export { PackHistory } from "./components/PackHistory/PackHistory";
export { Pagination } from "./components/Pagination/Pagination";
export { PinButton } from "./components/PinButton/PinButton";
export { PinnedBadge } from "./components/PinnedBadge/PinnedBadge";
export { PriceExplorer } from "./components/PriceExplorer/PriceExplorer";
export { PriceListItem } from "./components/PriceListItem/PriceListItem";
export { QuadrantRating } from "./components/QuadrantRating/QuadrantRating";
export { RarityFilter } from "./components/RarityFilter/RarityFilter";
export { RatingButtons } from "./components/RatingButtons/RatingButtons";
export { ResponseInput } from "./components/ResponseInput/ResponseInput";
export { TrafficLight } from "./components/TrafficLight/TrafficLight";
export { RatingSlider } from "./components/RatingSlider/RatingSlider";
export { RawJsonViewer } from "./components/RawJsonViewer/RawJsonViewer";
export { ScratchReveal } from "./components/ScratchReveal/ScratchReveal";
export { SearchInput } from "./components/SearchInput/SearchInput";
export { SetBadge } from "./components/SetBadge/SetBadge";
export { SimilarCardGrid } from "./components/SimilarCardGrid/SimilarCardGrid";
export { SimilarityScoreBadge } from "./components/SimilarityScoreBadge/SimilarityScoreBadge";
export { SetFlashcardGenerator } from "./components/SetFlashcardGenerator/SetFlashcardGenerator";
export { SetIcon } from "./components/SetIcon/SetIcon";
export { SortSelect } from "./components/SortSelect/SortSelect";
export { StatCard } from "./components/StatCard/StatCard";
export { StrategyPicker } from "./components/StrategyPicker/StrategyPicker";
export { StudyAnalytics } from "./components/StudyAnalytics/StudyAnalytics";
export { StudyDashboard } from "./components/StudyDashboard/StudyDashboard";
export { VectorHeatmap } from "./components/VectorHeatmap/VectorHeatmap";
export { VBarChart } from "./components/charts/VBarChart/VBarChart";
export { HBarChart } from "./components/charts/HBarChart/HBarChart";
export { DonutChart } from "./components/charts/DonutChart/DonutChart";
export { RadarChart } from "./components/charts/RadarChart/RadarChart";
export { LineChart } from "./components/charts/LineChart/LineChart";

// Flashcards app components
export { StudyHome } from "./components/StudyHome/StudyHome";
export { CollectionPicker } from "./components/CollectionPicker/CollectionPicker";
export { StudyFeed, StudyFeedEmpty, StudyFeedLoading } from "./components/StudyFeed/StudyFeed";
export { SetPicker } from "./components/SetPicker/SetPicker";
export { ManaValuePicker } from "./components/ManaValuePicker/ManaValuePicker";
export { RecallGuessForm } from "./components/RecallGuessForm/RecallGuessForm";
export type { RecallGuess } from "./components/RecallGuessForm/RecallGuessForm";
export { scoreRecallGuess } from "./components/RecallGuessForm/recallScorer";
export type { RecallScore, AspectScore } from "./components/RecallGuessForm/recallScorer";
export { TypeLinePicker } from "./components/TypeLinePicker/TypeLinePicker";
export { StatsPicker } from "./components/StatsPicker/StatsPicker";
export { OracleTextInput } from "./components/OracleTextInput/OracleTextInput";
export { ImageCarousel } from "./components/ImageCarousel/ImageCarousel";
export { GenerateButton } from "./components/GenerateButton/GenerateButton";
export { GenerateResult } from "./components/GenerateResult/GenerateResult";

// Layout components
export { CommandPaletteLayout } from "./components/CommandPaletteLayout/CommandPaletteLayout";
export { DualPanelLayout } from "./components/DualPanelLayout/DualPanelLayout";
export { FloatingNavLayout } from "./components/FloatingNavLayout/FloatingNavLayout";
export { HexLayout } from "./components/HexLayout/HexLayout";
export { MinimalLayout } from "./components/MinimalLayout/MinimalLayout";
export { RadialFanLayout } from "./components/RadialFanLayout/RadialFanLayout";
export { RadialLayout } from "./components/RadialLayout/RadialLayout";
export { RadialManaLayout } from "./components/RadialManaLayout/RadialManaLayout";
export { RadialOrbitalLayout } from "./components/RadialOrbitalLayout/RadialOrbitalLayout";
export { SidebarNav } from "./components/SidebarNav/SidebarNav";
export { TopNavLayout } from "./components/TopNavLayout/TopNavLayout";
export { TypographySpecimen } from "./components/TypographySpecimen/TypographySpecimen";
