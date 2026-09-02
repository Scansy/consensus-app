// The single Supabase client the whole app shares.
// Import it anywhere with:  import { supabase } from '@/lib/supabase';
//
// The URL and anon key come from the .env file (see .env.example). They are
// safe to ship inside the app — the anon key only allows what your Row Level
// Security policies allow. Never put the service_role key in here.

import 'react-native-url-polyfill/auto';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase env vars. Copy .env.example to .env and fill in ' +
      'EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY, then restart `npx expo start`.',
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    // store the logged-in session on the device so users stay signed in
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    // this is a URL-based thing that only applies on the web, not in a native app
    detectSessionInUrl: false,
  },
});
