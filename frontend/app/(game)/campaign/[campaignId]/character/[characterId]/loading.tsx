import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";

/**
 * Loading UI for the character sheet page.
 * Shown by Next.js while CharacterDetailPage is streaming or navigating.
 */
export default function CharacterDetailLoading(): React.ReactElement {
  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#F9F8F6" }}>
      {/* Header skeleton */}
      <Box
        sx={{
          px: { xs: 3, sm: 6 },
          py: 2,
          borderBottom: "1px solid #D9CFC7",
          bgcolor: "#EFE9E3",
        }}
      >
        <Skeleton variant="rounded" width={120} height={36} />
      </Box>

      {/* Content skeleton */}
      <Box sx={{ px: { xs: 3, sm: 6 }, py: 4, maxWidth: 720, mx: "auto" }}>
        {/* Name */}
        <Skeleton variant="rounded" width="60%" height={48} sx={{ mb: 2 }} />
        {/* Class + species chips */}
        <Box sx={{ display: "flex", gap: 1, mb: 4 }}>
          <Skeleton variant="rounded" width={90} height={28} />
          <Skeleton variant="rounded" width={90} height={28} />
        </Box>

        {/* Ability scores grid */}
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: 2,
            mb: 4,
          }}
        >
          {Array.from({ length: 6 }).map((_, i) => (
            // Index-based key is acceptable here: static list with no reordering.
            <Skeleton key={i} variant="rounded" height={100} />
          ))}
        </Box>

        {/* Background */}
        <Skeleton variant="rounded" width="40%" height={24} sx={{ mb: 1 }} />
        <Skeleton variant="rounded" height={72} sx={{ mb: 4 }} />

        {/* Traits */}
        <Skeleton variant="rounded" width="30%" height={24} sx={{ mb: 1 }} />
        <Skeleton variant="rounded" height={56} />
      </Box>
    </Box>
  );
}
