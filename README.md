# consensus-app

A mobile app that ends the "group chat planning abyss." Someone drops a prompt
("Study at the library tonight?"), everyone gets a quick poll instead of an
endless text thread, and the app locks in a time once the group reaches
consensus.

Built with **React Native + Expo (SDK 54)**. Backend is **Supabase**
(hosted Postgres database + auth), so there is no separate server to run —
the app talks to Supabase directly.

## Project layout

This is a plain Expo project. Everything lives at the repo root:

- `app/` — the screens (Expo Router file-based routing)
- `components/`, `hooks/`, `constants/` — reusable UI + theming
- `assets/` — images and icons
- `lib/` — shared setup, e.g. the Supabase client (added in the Supabase branch)

## Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Create your env file from the template and paste in the Supabase keys
   (get them from the Supabase dashboard: your project > Connect > Framework —
   you need to be invited to the project first):

   ```bash
   cp .env.example .env
   ```

   ```
   EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   EXPO_PUBLIC_SUPABASE_KEY=your-key
   ```

3. Start the dev server:

   ```bash
   npx expo start
   ```

4. On your phone, install **Expo Go** (App Store / Play Store), then:
   - **Android:** open Expo Go and scan the QR code in the terminal
   - **iOS:** scan the QR code with the Camera app (phone and laptop on the same Wi-Fi)

   Edit a file, save, and the change shows up on your phone in a second or two.

## Docs

- Expo (SDK 54): https://docs.expo.dev/versions/v54.0.0/
- Supabase with Expo / React Native: https://supabase.com/docs/guides/getting-started/tutorials/with-expo-react-native