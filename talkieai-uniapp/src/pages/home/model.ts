export interface Language {
  id?: string | null;
  language?: string | null;
  label: boolean;
  description?: string | null;
}

export interface Role {
  id?: string | null;
  local_name?: string|null;
  short_name: string;
  country: string;
  gender: string;
  avatar: string;
  audio: string;
  sequence: number;
  role_styles: string[];
}
