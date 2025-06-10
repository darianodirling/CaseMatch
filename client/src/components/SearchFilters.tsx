import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

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
      [key]: value === "all" ? "" : value,
    });
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
      {/* Assignment Group Filter */}
      <div className="relative">
        <Select
          value={filters.assignmentGroup || "all"}
          onValueChange={(value) => handleFilterChange('assignmentGroup', value)}
        >
          <SelectTrigger className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg shadow-material-1 focus:ring-2 focus:ring-material-blue focus:border-material-blue h-12">
            <SelectValue placeholder="Assignment Group" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Groups</SelectItem>
            <SelectItem value="database">Database Team</SelectItem>
            <SelectItem value="performance">Performance Team</SelectItem>
            <SelectItem value="security">Security Team</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Case Type Filter */}
      <div className="relative">
        <Select
          value={filters.caseType || "all"}
          onValueChange={(value) => handleFilterChange('caseType', value)}
        >
          <SelectTrigger className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg shadow-material-1 focus:ring-2 focus:ring-material-blue focus:border-material-blue h-12">
            <SelectValue placeholder="Case Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="bug">Bug Report</SelectItem>
            <SelectItem value="performance">Performance Issue</SelectItem>
            <SelectItem value="configuration">Configuration</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Date Filter */}
      <div className="relative">
        <Select
          value="all"
          onValueChange={() => {}}
        >
          <SelectTrigger className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg shadow-material-1 focus:ring-2 focus:ring-material-blue focus:border-material-blue h-12">
            <SelectValue placeholder="Date" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Dates</SelectItem>
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
          value={filters.status || "all"}
          onValueChange={(value) => handleFilterChange('status', value)}
        >
          <SelectTrigger className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg shadow-material-1 focus:ring-2 focus:ring-material-blue focus:border-material-blue h-12">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
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
