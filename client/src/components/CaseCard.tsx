import { Card } from "@/components/ui/card";
import type { Case } from "@shared/schema";

interface CaseCardProps {
  caseItem: Case;
  onClick: () => void;
  getSimilarityColor: (similarity: number) => string;
  getSimilarityBarColor: (similarity: number) => string;
}

export default function CaseCard({ 
  caseItem, 
  onClick, 
  getSimilarityColor, 
  getSimilarityBarColor 
}: CaseCardProps) {
  return (
    <Card
      className="bg-white rounded-lg shadow-material-1 hover:shadow-material-2 transition-all duration-200 cursor-pointer border border-gray-200"
      onClick={onClick}
    >
      <div className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="flex-1">
            {/* Case Number */}
            <h3 className="text-lg font-medium text-material-blue mb-3">
              {caseItem.number}
            </h3>
            
            {/* Description */}
            <p className="text-gray-900 font-medium mb-2">
              {caseItem.title}
            </p>
            
            {/* Resolution */}
            <p className="text-gray-600 text-sm leading-relaxed">
              {caseItem.resolution}
            </p>
          </div>
          
          {/* Similarity Score */}
          <div className="flex flex-col items-center sm:items-end">
            <div className={`text-2xl font-bold mb-1 ${getSimilarityColor(caseItem.similarity)}`}>
              {caseItem.similarity}%
            </div>
            <div className="w-20 bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${getSimilarityBarColor(caseItem.similarity)}`}
                style={{ width: `${caseItem.similarity}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 mt-1">Similarity</span>
          </div>
        </div>
      </div>
    </Card>
  );
}
