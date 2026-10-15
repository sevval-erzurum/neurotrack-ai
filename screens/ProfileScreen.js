import {
    Pressable,
    SafeAreaView,
    StyleSheet,
    Text,
    View,
} from "react-native";
  
  export default function ProfileScreen({ user, onBack }) {
    function getRoleText(role) {
      if (role === "adult") return "Yetişkin Kullanıcı";
      if (role === "parent") return "Ebeveyn";
      if (role === "doctor") return "Doktor";
      return "Kullanıcı";
    }
  
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.card}>
          <Text style={styles.title}>Profilim</Text>
  
          <View style={styles.infoBox}>
            <Text style={styles.label}>Kullanıcı ID</Text>
            <Text style={styles.value}>{user.user_id}</Text>
          </View>
  
          <View style={styles.infoBox}>
            <Text style={styles.label}>Ad Soyad</Text>
            <Text style={styles.value}>{user.full_name}</Text>
          </View>
  
          <View style={styles.infoBox}>
            <Text style={styles.label}>Email</Text>
            <Text style={styles.value}>{user.email}</Text>
          </View>
  
          <View style={styles.infoBox}>
            <Text style={styles.label}>Rol</Text>
            <Text style={styles.value}>{getRoleText(user.role)}</Text>
          </View>
  
          <Text style={styles.note}>
            Bu ID bilgisi, doktorun hastayı sisteme ekleyebilmesi için kullanılabilir.
          </Text>
  
          <Pressable style={styles.backButton} onPress={onBack}>
            <Text style={styles.buttonText}>Geri Dön</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }
  
  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: "#F3F4F6",
      justifyContent: "center",
      padding: 24,
    },
    card: {
      backgroundColor: "#FFFFFF",
      padding: 24,
      borderRadius: 18,
    },
    title: {
      fontSize: 26,
      fontWeight: "700",
      color: "#111827",
      textAlign: "center",
      marginBottom: 20,
    },
    infoBox: {
      backgroundColor: "#EFF6FF",
      padding: 14,
      borderRadius: 12,
      marginBottom: 12,
    },
    label: {
      color: "#6B7280",
      fontSize: 13,
      marginBottom: 4,
    },
    value: {
      color: "#111827",
      fontSize: 17,
      fontWeight: "700",
    },
    note: {
      color: "#6B7280",
      fontSize: 13,
      textAlign: "center",
      lineHeight: 20,
      marginTop: 8,
      marginBottom: 18,
    },
    backButton: {
      backgroundColor: "#374151",
      padding: 14,
      borderRadius: 12,
      alignItems: "center",
    },
    buttonText: {
      color: "#FFFFFF",
      fontSize: 16,
      fontWeight: "700",
    },
  });