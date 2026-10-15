import { useEffect, useRef, useState } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { sendChatMessage } from "../services/api";

export default function ChatbotScreen({ user, onBack }) {
  const scrollRef = useRef(null);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  function getRoleLabel(role) {
    if (role === "adult") return "yetişkin kullanıcı";
    if (role === "parent") return "ebeveyn";
    if (role === "doctor") return "doktor";
    return "kullanıcı";
  }

  function getWelcomeMessage() {
    if (user.role === "doctor") {
      return "Merhaba, ben DEVA. Bugün hasta takibi, klinik yorumlama veya kayıt analizi konusunda sana nasıl yardımcı olabilirim?";
    }

    if (user.role === "parent") {
      return "Merhaba, ben DEVA. Bugün çocuğunla ilgili takip, günlük kayıt veya uyarı analizi konusunda sana nasıl yardımcı olabilirim?";
    }

    return "Merhaba, ben DEVA. Bugün günlük takip, duygu durumu, risk analizi veya öneriler konusunda sana nasıl yardımcı olabilirim?";
  }

  useEffect(() => {
    setMessages([
      {
        id: Date.now(),
        sender: "ai",
        text: getWelcomeMessage(),
      },
    ]);
  }, []);

  useEffect(() => {
    setTimeout(() => {
      scrollRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, [messages, isTyping]);

  async function handleSend() {
    const cleanText = input.trim();

    if (!cleanText) {
      return;
    }

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: cleanText,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const { response, data } = await sendChatMessage(
        user.user_id,
        cleanText,
        user.role
      );

      let aiText = "";

      if (response.ok) {
        aiText =
          data.reply ||
          data.message ||
          data.answer ||
          "Yanıt oluşturuldu ancak cevap metni alınamadı.";
      } else {
        aiText = data.detail
          ? String(data.detail)
          : "DEVA şu anda yanıt oluşturamadı.";
      }

      const aiMessage = {
        id: Date.now() + 1,
        sender: "ai",
        text: aiText,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          sender: "ai",
          text: "Şu anda bağlantı sorunu yaşıyorum. Backend açık mı kontrol edebilir misin?",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboardContainer}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>DEVA AI Asistan</Text>
            <Text style={styles.subtitle}>
              {user.full_name} • {getRoleLabel(user.role)}
            </Text>
          </View>

          <Pressable style={styles.backButtonSmall} onPress={onBack}>
            <Text style={styles.backButtonSmallText}>Geri</Text>
          </Pressable>
        </View>

        <ScrollView
          ref={scrollRef}
          style={styles.chatArea}
          contentContainerStyle={styles.chatContent}
        >
          {messages.map((item) => {
            const isUser = item.sender === "user";

            return (
              <View
                key={item.id}
                style={isUser ? styles.userBubble : styles.aiBubble}
              >
                <Text style={styles.senderText}>
                  {isUser ? "Sen" : "DEVA"}
                </Text>

                <Text style={isUser ? styles.userMessageText : styles.aiMessageText}>
                  {item.text}
                </Text>
              </View>
            );
          })}

          {isTyping && (
            <View style={styles.aiBubble}>
              <Text style={styles.senderText}>DEVA</Text>
              <Text style={styles.aiMessageText}>Yazıyor...</Text>
            </View>
          )}
        </ScrollView>

        <View style={styles.inputArea}>
          <TextInput
            placeholder="DEVA'ya mesaj yaz..."
            placeholderTextColor="#6B7280"
            value={input}
            onChangeText={setInput}
            style={styles.input}
            multiline
          />

          <Pressable style={styles.sendButton} onPress={handleSend}>
            <Text style={styles.sendButtonText}>Gönder</Text>
          </Pressable>
        </View>

        <Text style={styles.disclaimer}>
          DEVA tanı koymaz. Sadece takip, bilgilendirme ve karar desteği amacıyla yardımcı olur.
        </Text>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
  },
  keyboardContainer: {
    flex: 1,
    padding: 16,
  },
  header: {
    backgroundColor: "#FFFFFF",
    borderRadius: 18,
    padding: 16,
    marginBottom: 12,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  title: {
    fontSize: 21,
    fontWeight: "900",
    color: "#111827",
  },
  subtitle: {
    fontSize: 13,
    color: "#6B7280",
    marginTop: 3,
  },
  backButtonSmall: {
    backgroundColor: "#374151",
    paddingVertical: 9,
    paddingHorizontal: 13,
    borderRadius: 10,
  },
  backButtonSmallText: {
    color: "#FFFFFF",
    fontWeight: "900",
  },
  chatArea: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    borderRadius: 18,
    paddingHorizontal: 10,
    paddingTop: 10,
  },
  chatContent: {
    paddingBottom: 12,
  },
  aiBubble: {
    alignSelf: "flex-start",
    backgroundColor: "#F5F3FF",
    borderWidth: 1,
    borderColor: "#DDD6FE",
    padding: 13,
    borderRadius: 16,
    marginBottom: 10,
    maxWidth: "85%",
  },
  userBubble: {
    alignSelf: "flex-end",
    backgroundColor: "#DBEAFE",
    borderWidth: 1,
    borderColor: "#BFDBFE",
    padding: 13,
    borderRadius: 16,
    marginBottom: 10,
    maxWidth: "85%",
  },
  senderText: {
    fontSize: 12,
    fontWeight: "900",
    color: "#374151",
    marginBottom: 5,
  },
  aiMessageText: {
    fontSize: 15,
    color: "#111827",
    lineHeight: 22,
  },
  userMessageText: {
    fontSize: 15,
    color: "#111827",
    lineHeight: 22,
  },
  inputArea: {
    backgroundColor: "#FFFFFF",
    borderRadius: 18,
    padding: 10,
    marginTop: 12,
    flexDirection: "row",
    alignItems: "flex-end",
    gap: 8,
  },
  input: {
    flex: 1,
    minHeight: 44,
    maxHeight: 110,
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 13,
    padding: 11,
    color: "#111827",
    fontSize: 15,
  },
  sendButton: {
    backgroundColor: "#7C3AED",
    paddingVertical: 13,
    paddingHorizontal: 14,
    borderRadius: 13,
  },
  sendButtonText: {
    color: "#FFFFFF",
    fontWeight: "900",
  },
  disclaimer: {
    fontSize: 11,
    color: "#6B7280",
    textAlign: "center",
    marginTop: 8,
    lineHeight: 16,
  },
});