import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ChevronDown } from "lucide-react";

interface SearchFiltersProps {
  filters: {
    assignmentGroup: string;
    caseType: string;
    status: string;
  };
  onFiltersChange: (filters: {
    assignmentGroup: string;
    caseType: string;
    status: string;
  }) => void;
}

export default function SearchFilters({ filters, onFiltersChange }: SearchFiltersProps) {
  const handleFilterChange = (key: string, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    });
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
      {/* Assignment Group Filter */}
      <div className="relative">
        <Select
          value={filters.assignmentGroup}
          onValueChange={(value) => handleFilterChange('assignmentGroup', value)}
        >
          <SelectTrigger className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg shadow-material-1 focus:ring-2 focus:ring-material-blue focus:border-material-blue h-12">
            <SelectValue placeholder="Assignment Group" />
            <ChevronDown className="h-4 w-4 opacity-50" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Groups</SelectItem>
            <SelectItem value="database">Database Team</SelectItem>
            <SelectItem value="performance">Performance Team</SelectItem>
            <SelectItem value="security">Security Team</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Case Type Filter */}
      <div className="relative">
        <Select
          value={filters.caseType}
          onValueChange={(value) => handleFilterChange('caseType', value)}
        >
          <SelectTrigger className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg shadow-material-1 focus:ring-2 focus:ring-material-blue focus:border-material-blue h-12">
            <SelectValue placeholder="Case Type" />
            <ChevronDown className="h-4 w-4 opacity-50" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Types</SelectItem>
            <SelectItem value="bug">Bug Report</SelectItem>
            <SelectItem value="performance">Performance Issue</SelectItem>
            <SelectItem value="configuration">Configuration</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Date Filter */}
      <div className="relative">
        <Select
          value=""
          onValueChange={() => {}}
        >
          <SelectTrigger className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg shadow-material-1 focus:ring-2 focus:ring-material-blue focus:border-material-blue h-12">
            <SelectValue placeholder="Date" />
            <ChevronDown className="h-4 w-4 opacity-50" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="today">Today</SelectItem>
            <SelectItem value="week">This Week</SelectItem>
            <SelectItem value="month">This Month</SelectItem>
            <SelectItem value="quarter">This Quarter</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Status Filter */}
      <div className="relative">
        <Select
          value={filters.status}
          onValueChange={(value) => handleFilterChange('status', value)}
        >
          <SelectTrigger className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg shadow-material-1 focus:ring-2 focus:ring-material-blue focus:border-material-blue h-12">
            <SelectValue placeholder="Status" />
            <ChevronDown className="h-4 w-4 opacity-50" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Statuses</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="in-progress">In Progress</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
