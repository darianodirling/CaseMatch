import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Search, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { apiRequest } from "@/lib/queryClient";

interface SimilarCase {
  case_number: string;
  similarity_score: number;
  title: string;
  resolution: string;
  assignment_group: string;
  case_type: string;
  status: string;
}

interface SimilaritySearchResponse {
  success: boolean;
  case_number: string;
  similar_cases: SimilarCase[];
  total_found: number;
  error?: string;
}

export default function SimilaritySearch() {
  const [searchInput, setSearchInput] = useState("");
  const [results, setResults] = useState<SimilarCase[]>([]);
  const [searchedCase, setSearchedCase] = useState("");

  const searchMutation = useMutation({
    mutationFn: async (caseNumber: string): Promise<SimilaritySearchResponse> => {
      const response = await fetch('http://localhost:5001/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_number: caseNumber,
          top_k: 5
        })
      });
      
      if (!response.ok) {
        throw new Error(`Backend request failed: ${response.status}`);
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      if (data.success) {
        setResults(data.similar_cases);
        setSearchedCase(data.case_number);
      }
    }
  });

  const handleSearch = () => {
    const caseNumber = searchInput.trim();
    if (!caseNumber) return;
    
    searchMutation.mutate(caseNumber);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getSimilarityColor = (similarity: number) => {
    const score = Math.round(similarity * 100);
    if (score >= 90) return "text-green-600";
    if (score >= 80) return "text-yellow-600";
    return "text-orange-600";
  };

  const getSimilarityBarColor = (similarity: number) => {
    const score = Math.round(similarity * 100);
    if (score >= 90) return "bg-green-500";
    if (score >= 80) return "bg-yellow-500";
    return "bg-orange-500";
  };

  return (
    <div className="space-y-6">
      {/* Search Section */}
      <div className="bg-white rounded-lg shadow-material-1 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          AI-Powered Case Similarity Search
        </h2>
        <p className="text-gray-600 mb-4">
          Enter a case number to find similar cases using machine learning analysis of case descriptions and resolutions.
        </p>
        
        <div className="flex space-x-3">
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <Input
              type="text"
              placeholder="Enter case number (e.g., CS10023856)"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="pl-10"
              disabled={searchMutation.isPending}
            />
          </div>
          <Button 
            onClick={handleSearch}
            disabled={searchMutation.isPending || !searchInput.trim()}
            className="bg-material-blue hover:bg-material-blue/90"
          >
            {searchMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Search
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {searchMutation.isError && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            {searchMutation.error instanceof Error 
              ? `Search failed: ${searchMutation.error.message}. Please ensure the Flask backend is running on port 5001.`
              : 'An error occurred while searching for similar cases.'
            }
          </AlertDescription>
        </Alert>
      )}

      {/* Results Section */}
      {searchedCase && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              Similar Cases for {searchedCase}
            </h3>
            <span className="text-sm text-gray-500">
              {results.length} similar cases found
            </span>
          </div>

          {results.length === 0 && !searchMutation.isPending && (
            <Card className="p-6 text-center">
              <div className="text-gray-500">
                <Search className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No similar cases found for {searchedCase}</p>
                <p className="text-sm mt-1">Try a different case number or check if the case exists in the system.</p>
              </div>
            </Card>
          )}

          {results.map((similarCase, index) => (
            <Card
              key={similarCase.case_number}
              className="bg-white rounded-lg shadow-material-1 hover:shadow-material-2 transition-all duration-200 cursor-pointer border border-gray-200"
              onClick={() => {
                // You can implement navigation to case details here
                console.log('Navigate to case:', similarCase.case_number);
              }}
            >
              <div className="p-6">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                  <div className="flex-1">
                    {/* Case Number and Rank */}
                    <div className="flex items-center space-x-2 mb-3">
                      <span className="bg-material-blue text-white text-xs px-2 py-1 rounded">
                        #{index + 1}
                      </span>
                      <h4 className="text-lg font-medium text-material-blue">
                        {similarCase.case_number}
                      </h4>
                    </div>
                    
                    {/* Title */}
                    <p className="text-gray-900 font-medium mb-2">
                      {similarCase.title}
                    </p>
                    
                    {/* Resolution */}
                    <p className="text-gray-600 text-sm leading-relaxed mb-3">
                      {similarCase.resolution}
                    </p>

                    {/* Metadata */}
                    <div className="flex flex-wrap gap-2 text-xs">
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {similarCase.assignment_group}
                      </span>
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {similarCase.case_type}
                      </span>
                      <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {similarCase.status}
                      </span>
                    </div>
                  </div>
                  
                  {/* Similarity Score */}
                  <div className="flex flex-col items-center sm:items-end">
                    <div className={`text-2xl font-bold mb-1 ${getSimilarityColor(similarCase.similarity_score)}`}>
                      {Math.round(similarCase.similarity_score * 100)}%
                    </div>
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${getSimilarityBarColor(similarCase.similarity_score)}`}
                        style={{ width: `${Math.round(similarCase.similarity_score * 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 mt-1">Similarity</span>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}