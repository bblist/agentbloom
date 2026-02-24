/**
 * DiceBear Avatar Utility
 * Generates unique, beautiful avatars via the DiceBear API.
 * https://www.dicebear.com/
 *
 * Styles used:
 *  - bottts: Robot avatars (agent/AI)
 *  - notionists: Modern illustrated people (users, contacts)
 *  - glass: Glossy abstract shapes (thumbnails, cards)
 *  - shapes: Geometric patterns (decorative, stats)
 *  - rings: Concentric ring patterns (empty states)
 *  - thumbs: Cute thumbs (reactions, success)
 *  - identicon: Unique geometric identicons (nav, generic)
 *  - initials: Letter-based avatars (fallback for names)
 */

export type DiceBearStyle =
  | "bottts"
  | "bottts-neutral"
  | "notionists"
  | "notionists-neutral"
  | "glass"
  | "shapes"
  | "rings"
  | "thumbs"
  | "identicon"
  | "initials"
  | "adventurer"
  | "adventurer-neutral"
  | "avataaars"
  | "avataaars-neutral"
  | "big-ears"
  | "big-ears-neutral"
  | "big-smile"
  | "croodles"
  | "croodles-neutral"
  | "dylan"
  | "fun-emoji"
  | "icons"
  | "lorelei"
  | "lorelei-neutral"
  | "micah"
  | "miniavs"
  | "open-peeps"
  | "personas"
  | "pixel-art"
  | "pixel-art-neutral";

const DICEBEAR_BASE = "https://api.dicebear.com/9.x";

interface AvatarOptions {
  seed?: string;
  size?: number;
  backgroundColor?: string[];
  backgroundType?: "solid" | "gradientLinear";
  radius?: number;
  flip?: boolean;
  rotate?: number;
  scale?: number;
}

/**
 * Generate a DiceBear avatar URL
 */
export function dicebear(
  style: DiceBearStyle,
  seed: string,
  options: AvatarOptions = {}
): string {
  const params = new URLSearchParams();
  params.set("seed", seed);

  if (options.size) params.set("size", options.size.toString());
  if (options.backgroundColor?.length) {
    params.set("backgroundColor", options.backgroundColor.join(","));
  }
  if (options.backgroundType) params.set("backgroundType", options.backgroundType);
  if (options.radius !== undefined) params.set("radius", options.radius.toString());
  if (options.flip) params.set("flip", "true");
  if (options.rotate) params.set("rotate", options.rotate.toString());
  if (options.scale) params.set("scale", options.scale.toString());

  return `${DICEBEAR_BASE}/${style}/svg?${params.toString()}`;
}

// ─── Preset helpers ───────────────────────────────────────────────────────

/** Robot avatar for the AI agent */
export function agentAvatar(seed = "agentbloom-ai") {
  return dicebear("bottts", seed, {
    backgroundColor: ["b6e3f4", "c0aede", "d1d4f9"],
    backgroundType: "gradientLinear",
    radius: 50,
  });
}

/** User/people avatar */
export function userAvatar(seed: string) {
  return dicebear("notionists", seed, {
    backgroundColor: ["b6e3f4", "c0aede", "d1d4f9", "ffd5dc", "ffdfbf"],
    backgroundType: "solid",
    radius: 50,
  });
}

/** Contact avatar (CRM) — more colorful variant */
export function contactAvatar(seed: string) {
  return dicebear("adventurer", seed, {
    backgroundColor: ["b6e3f4", "c0aede", "d1d4f9", "ffd5dc", "ffdfbf"],
    backgroundType: "solid",
    radius: 50,
  });
}

/** Glass/gradient thumbnail for sites/courses */
export function thumbnailAvatar(seed: string) {
  return dicebear("glass", seed, {
    radius: 12,
  });
}

/** Geometric shape for stats/cards */
export function shapeIcon(seed: string) {
  return dicebear("shapes", seed, {
    radius: 12,
    size: 48,
  });
}

/** Navigation icons — identicon style */
export function navIcon(seed: string) {
  return dicebear("bottts-neutral", seed, {
    radius: 8,
    size: 28,
  });
}

/** Rings for empty states */
export function emptyStateAvatar(seed: string) {
  return dicebear("rings", seed, {
    size: 80,
  });
}

/** Initials avatar */
export function initialsAvatar(name: string) {
  return dicebear("initials", name, {
    backgroundColor: ["3b82f6", "10b981", "8b5cf6", "f59e0b", "ef4444"],
    backgroundType: "solid",
    radius: 50,
    size: 48,
  });
}
