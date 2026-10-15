import { StyleSheet, Text, View } from "react-native";

const COLORS = {
  primary: "#2563EB",
  white: "#FFFFFF",
  dark: "#111827",
  gray: "#6B7280",
  blueSoft: "#EFF6FF",
};

export default function AppBrandHeader({ small = false }) {
  return (
    <View style={styles.container}>
      <View style={styles.logoCircle}>
        <Text style={styles.logoText}>N</Text>
      </View>

      <Text style={small ? styles.smallTitle : styles.title}>
        NeuroTrack AI
      </Text>

      <Text style={styles.subtitle}>
        Otizm Takip ve Karar Destek Sistemi
      </Text>

      <View style={styles.badge}>
        <Text style={styles.badgeText}>AI Destekli Klinik Takip</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    marginBottom: 22,
  },
  logoCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: COLORS.primary,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 12,
  },
  logoText: {
    color: COLORS.white,
    fontSize: 30,
    fontWeight: "900",
  },
  title: {
    fontSize: 28,
    fontWeight: "900",
    color: COLORS.dark,
    textAlign: "center",
  },
  smallTitle: {
    fontSize: 24,
    fontWeight: "900",
    color: COLORS.dark,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 14,
    color: COLORS.gray,
    textAlign: "center",
    marginTop: 4,
  },
  badge: {
    backgroundColor: COLORS.blueSoft,
    paddingVertical: 7,
    paddingHorizontal: 14,
    borderRadius: 999,
    marginTop: 12,
  },
  badgeText: {
    color: COLORS.primary,
    fontSize: 12,
    fontWeight: "800",
  },
});