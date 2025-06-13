import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Sparkles } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import CaseCard from "@/components/CaseCard";
import SearchFilters from "@/components/SearchFilters";
import SimilaritySearch from "@/components/SimilaritySearch";
import type { Case } from "@shared/schema";

export default function Dashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState({
    assignmentGroup: "",
    caseType: "",
    status: "",
  });
  const [debouncedQuery, setDebouncedQuery] = useState("");

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Build API endpoint based on filters and search
  const buildApiEndpoint = () => {
    const hasFilters = Object.values(filters).some(value => value !== "");
    const hasSearch = debouncedQuery.trim() !== "";

    if (hasSearch && hasFilters) {
      // For complex queries, we'll need to implement a combined endpoint
      // For now, prioritize search over filters
      return `/api/cases/search?q=${encodeURIComponent(debouncedQuery)}`;
    } else if (hasSearch) {
      return `/api/cases/search?q=${encodeURIComponent(debouncedQuery)}`;
    } else if (hasFilters) {
      const params = new URLSearchParams();
      if (filters.assignmentGroup) params.append('assignmentGroup', filters.assignmentGroup);
      if (filters.caseType) params.append('caseType', filters.caseType);
      if (filters.status) params.append('status', filters.status);
      return `/api/cases/filter?${params.toString()}`;
    } else {
      return '/api/cases';
    }
  };

  const { data: cases, isLoading, error } = useQuery<Case[]>({
    queryKey: [buildApiEndpoint()],
    staleTime: 30000,
  });

  const handleCaseClick = (caseItem: Case) => {
    window.open(caseItem.externalUrl, '_blank', 'noopener,noreferrer');
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 90) return "text-green-600";
    if (similarity >= 85) return "text-green-500";
    if (similarity >= 80) return "text-yellow-600";
    return "text-orange-600";
  };

  const getSimilarityBarColor = (similarity: number) => {
    if (similarity >= 90) return "bg-green-500";
    if (similarity >= 85) return "bg-green-400";
    if (similarity >= 80) return "bg-yellow-500";
    return "bg-orange-500";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              {/* SAS Logo */}
              <div className="w-12 h-8 bg-sas-blue rounded flex items-center justify-center">
                <span className="text-white font-bold text-sm">SAS</span>
              </div>
              <h1 className="text-xl font-medium text-gray-900">CaseMatch</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-light text-gray-900 mb-8">CaseMatch</h1>
          
          {/* Tab Navigation */}
          <Tabs defaultValue="search" className="w-full">
            <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
              <TabsTrigger value="search" className="flex items-center space-x-2">
                <Search className="h-4 w-4" />
                <span>Case Search</span>
              </TabsTrigger>
              <TabsTrigger value="similarity" className="flex items-center space-x-2">
                <Sparkles className="h-4 w-4" />
                <span>AI Similarity</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="search" className="space-y-8">
              {/* Traditional Search Bar */}
              <div className="max-w-2xl mx-auto">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                  </div>
                  <Input
                    type="text"
                    placeholder="Search cases..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-12 pr-4 py-4 text-lg border border-gray-300 rounded-lg bg-white shadow-material-1 focus:ring-2 focus:ring-material-blue focus:border-material-blue transition-all duration-200 h-14"
                  />
                </div>
              </div>

              {/* Filter Dropdowns */}
              <SearchFilters filters={filters} onFiltersChange={setFilters} />

              {/* Search Results */}
              <div className="space-y-4">
                {isLoading && (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="bg-white rounded-lg shadow-material-1 p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <Skeleton className="h-6 w-32 mb-3" />
                            <Skeleton className="h-4 w-full mb-2" />
                            <Skeleton className="h-3 w-3/4" />
                          </div>
                          <div className="flex flex-col items-end">
                            <Skeleton className="h-8 w-12 mb-1" />
                            <Skeleton className="h-2 w-20" />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {error && (
                  <div className="text-center py-12">
                    <div className="text-red-500 text-lg font-medium mb-2">Error loading cases</div>
                    <p className="text-gray-500">Please try again later</p>
                  </div>
                )}

                {!isLoading && !error && cases && cases.length === 0 && (
                  <div className="text-center py-12">
                    <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No cases found</h3>
                    <p className="text-gray-500">Try adjusting your search terms or filters</p>
                  </div>
                )}

                {!isLoading && !error && cases && cases.length > 0 && (
                  <>
                    {cases.map((caseItem) => (
                      <CaseCard
                        key={caseItem.id}
                        caseItem={caseItem}
                        onClick={() => handleCaseClick(caseItem)}
                        getSimilarityColor={getSimilarityColor}
                        getSimilarityBarColor={getSimilarityBarColor}
                      />
                    ))}
                  </>
                )}
              </div>
            </TabsContent>

            <TabsContent value="similarity">
              <SimilaritySearch />
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}
