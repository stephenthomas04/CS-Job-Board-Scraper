// Mirrors the schema in ../../current_processor.py 1:1.
export interface Job {
  source: string;
  company_name: string;
  company_url: string;
  id: string;
  title: string;
  url: string;
  locations: string[];
  season: string;
  // "" => sponsorship available/unknown
  // "Does Not Offer Sponsorship" | "U.S. Citizenship is Required"
  sponsorship: string;
  active: boolean;
  is_visible: boolean;
  date_posted: number; // epoch seconds
  date_updated: number; // epoch seconds
}
