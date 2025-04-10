import React, { useState, useEffect, useRef } from "react";
import {
  Layout,
  Input,
  Button,
  Spin,
  message,
  Drawer,
  List,
  Modal,
  Form,
  Radio,
  Alert,
  Select,
  Avatar,
  Popconfirm,
  Badge,
  Tooltip,
} from "antd";
import {
  SendOutlined,
  SaveOutlined,
  LoadingOutlined,
  ClearOutlined,
  MenuOutlined,
  FileImageOutlined,
  UserSwitchOutlined,
  RobotOutlined,
  GlobalOutlined,
  DeleteOutlined,
  PlusCircleOutlined,
  ApiOutlined,
  LinkOutlined,
  DisconnectOutlined,
} from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import axios from "axios";
import "./App.css";
import RoleSelector from "./components/RoleSelector";

// 创建一个空的模型列表，稍后从后端获取
const availableModels = [];

const { Header, Content, Footer } = Layout;
const { TextArea } = Input;
const { Option } = Select;

// 创建axios实例
const api = axios.create();

function App() {
  const [messageInput, setMessageInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [saveTitle, setSaveTitle] = useState("");
  const [imageModalVisible, setImageModalVisible] = useState(false);
  const [imagePrompt, setImagePrompt] = useState("");
  const [imageSize, setImageSize] = useState("1024x1024");
  const [generatingImage, setGeneratingImage] = useState(false);
  const [imageUrl, setImageUrl] = useState("");
  const [apiConnected, setApiConnected] = useState(false);
  const [apiBaseUrl, setApiBaseUrl] = useState("");
  const [apiChecking, setApiChecking] = useState(true);
  const [roleSelected, setRoleSelected] = useState(false);
  const [currentRole, setCurrentRole] = useState(null);
  const [roleModalVisible, setRoleModalVisible] = useState(false);
  const [selectedModel, setSelectedModel] = useState(""); // 初始为空字符串，等待从后端获取默认值
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [imageModel, setImageModel] = useState("dall-e-3");
  const [imageQuality, setImageQuality] = useState("standard");
  const [imageStyle, setImageStyle] = useState("vivid");
  const [revisedPrompt, setRevisedPrompt] = useState("");
  // 添加新的状态变量，用于存储从后端获取的模型列表
  const [modelsByCategory, setModelsByCategory] = useState({});
  // 添加MCP相关状态
  const [mcpServers, setMcpServers] = useState([]);
  const [mcpModalVisible, setMcpModalVisible] = useState(false);
  const [loadingMcpServers, setLoadingMcpServers] = useState(false);
  const [mcpAddModalVisible, setMcpAddModalVisible] = useState(false);
  const [newMcpServer, setNewMcpServer] = useState({
    id: "",
    config: { url: "" },
  });
  const [mcpConnecting, setMcpConnecting] = useState({});
  const [mcpErrorMessage, setMcpErrorMessage] = useState("");

  const messagesEndRef = useRef(null);
  const [form] = Form.useForm();
  const [imageForm] = Form.useForm();
  const [mcpForm] = Form.useForm();

  // 检查API服务器连接
  useEffect(() => {
    const checkApiConnection = async () => {
      setApiChecking(true);

      // 只尝试连接端口5001
      const connected = await tryConnectToPort(5001);

      setApiChecking(false);
    };

    const tryConnectToPort = async (port) => {
      const baseUrl = `http://localhost:${port}`;
      try {
        // 尝试连接API服务器
        const response = await fetch(`${baseUrl}/api/conversations/clear`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (response.ok) {
          console.log(`成功连接到API服务器: ${baseUrl}`);
          setApiBaseUrl(baseUrl);
          api.defaults.baseURL = baseUrl;
          setApiConnected(true);

          // 获取当前角色
          try {
            const roleResponse = await fetch(`${baseUrl}/api/role`);
            if (roleResponse.ok) {
              const roleData = await roleResponse.json();
              setCurrentRole({
                role: roleData.current_role,
                system_content:
                  roleData.predefined_roles[roleData.current_role],
              });
            }
          } catch (error) {
            console.error("获取角色失败:", error);
          }

          // 获取模型列表
          try {
            const modelsResponse = await fetch(`${baseUrl}/api/models`);
            if (modelsResponse.ok) {
              const modelsData = await modelsResponse.json();

              // 清空现有模型列表
              availableModels.length = 0;

              // 设置默认模型
              if (modelsData.default_model) {
                setSelectedModel(modelsData.default_model);
              }

              // 将模型按类别整理为前端需要的格式
              const modelsByCategoryData = modelsData.models_by_category || {};
              setModelsByCategory(modelsByCategoryData);

              Object.keys(modelsByCategoryData).forEach((category) => {
                const categoryModels = modelsByCategoryData[category];
                categoryModels.forEach((modelData) => {
                  // 判断模型是否支持联网，默认OpenAI、Google和Anthropic模型支持联网
                  const hasInternet = [
                    "OpenAI",
                    "OpenAI多模态",
                    "Google",
                    "Anthropic",
                  ].includes(category);

                  availableModels.push({
                    value: modelData.id,
                    label: modelData.id
                      .split("-")
                      .map(
                        (word) => word.charAt(0).toUpperCase() + word.slice(1)
                      )
                      .join(" "),
                    hasInternet: hasInternet,
                    description: modelData.description || "",
                    category: category,
                  });
                });
              });

              // 强制更新组件
              setSelectedModel((prev) => prev);
            }
          } catch (error) {
            console.error("获取模型列表失败:", error);
          }

          // 获取MCP服务器列表
          loadMcpServers();

          return true;
        }
      } catch (error) {
        console.log(`无法连接到端口 ${port}: ${error.message}`);
      }
      return false;
    };

    checkApiConnection();
  }, []);

  // 加载MCP服务器列表
  const loadMcpServers = async () => {
    if (!apiConnected) return;

    setLoadingMcpServers(true);
    setMcpErrorMessage("");
    try {
      const response = await api.get("/api/mcp/servers");
      setMcpServers(response.data.servers || []);
    } catch (error) {
      console.error("加载MCP服务器列表失败:", error);
      setMcpErrorMessage(
        "加载MCP服务器列表失败: " +
          (error.response?.data?.error || error.message)
      );
    } finally {
      setLoadingMcpServers(false);
    }
  };

  // 连接到MCP服务器
  const connectToMcpServer = async (serverId) => {
    if (!apiConnected) return;

    setMcpConnecting((prev) => ({ ...prev, [serverId]: true }));
    setMcpErrorMessage("");
    try {
      const response = await api.post(`/api/mcp/servers/${serverId}/connect`);
      if (response.data.success) {
        message.success(`已连接到MCP服务器: ${serverId}`);
        // 更新服务器状态
        loadMcpServers();
      } else {
        message.error(`连接MCP服务器失败: ${serverId}`);
        setMcpErrorMessage(
          `连接MCP服务器失败: ${response.data.error || "未知错误"}`
        );
      }
    } catch (error) {
      console.error(`连接MCP服务器失败: ${serverId}`, error);
      message.error(`连接MCP服务器失败: ${serverId}`);
      setMcpErrorMessage(
        `连接MCP服务器失败: ${error.response?.data?.error || error.message}`
      );
    } finally {
      setMcpConnecting((prev) => ({ ...prev, [serverId]: false }));
    }
  };

  // 断开与MCP服务器的连接
  const disconnectFromMcpServer = async (serverId) => {
    if (!apiConnected) return;

    setMcpConnecting((prev) => ({ ...prev, [serverId]: true }));
    setMcpErrorMessage("");

    try {
      const response = await api.post(
        `/api/mcp/servers/${serverId}/disconnect`
      );

      if (response.data.success) {
        message.success(`已断开与MCP服务器的连接: ${serverId}`);
        // 更新服务器状态
        loadMcpServers();
      } else {
        message.error(`断开MCP服务器连接失败: ${serverId}`);
        setMcpErrorMessage(
          `断开MCP服务器连接失败: ${response.data.error || "未知错误"}`
        );
      }
    } catch (error) {
      console.error(`断开MCP服务器连接失败: ${serverId}`, error);
      message.error(`断开MCP服务器连接失败: ${serverId}`);
      setMcpErrorMessage(
        `断开MCP服务器连接失败: ${error.response?.data?.error || error.message}`
      );
    } finally {
      setMcpConnecting((prev) => ({ ...prev, [serverId]: false }));
    }
  };

  // 添加MCP服务器
  const addMcpServer = async () => {
    if (!apiConnected) return;

    if (!newMcpServer.id || !newMcpServer.config.url) {
      message.error("服务器ID和URL不能为空");
      return;
    }

    setLoadingMcpServers(true);
    setMcpErrorMessage("");

    try {
      const response = await api.post("/api/mcp/servers", newMcpServer);

      if (response.data.success) {
        message.success(`已添加MCP服务器: ${newMcpServer.id}`);
        // 重置表单
        setNewMcpServer({ id: "", config: { url: "" } });
        // 关闭添加模态框
        setMcpAddModalVisible(false);
        // 更新服务器列表
        loadMcpServers();
      } else {
        message.error(`添加MCP服务器失败: ${newMcpServer.id}`);
        setMcpErrorMessage(
          `添加MCP服务器失败: ${response.data.error || "未知错误"}`
        );
      }
    } catch (error) {
      console.error(`添加MCP服务器失败: ${newMcpServer.id}`, error);
      message.error(`添加MCP服务器失败: ${newMcpServer.id}`);
      setMcpErrorMessage(
        `添加MCP服务器失败: ${error.response?.data?.error || error.message}`
      );
    } finally {
      setLoadingMcpServers(false);
    }
  };

  // 删除MCP服务器
  const deleteMcpServer = async (serverId) => {
    if (!apiConnected) return;

    setLoadingMcpServers(true);
    setMcpErrorMessage("");

    try {
      const response = await api.delete(`/api/mcp/servers/${serverId}`);

      if (response.data.success) {
        message.success(`已删除MCP服务器: ${serverId}`);
        // 更新服务器列表
        loadMcpServers();
      } else {
        message.error(`删除MCP服务器失败: ${serverId}`);
        setMcpErrorMessage(
          `删除MCP服务器失败: ${response.data.error || "未知错误"}`
        );
      }
    } catch (error) {
      console.error(`删除MCP服务器失败: ${serverId}`, error);
      message.error(`删除MCP服务器失败: ${serverId}`);
      setMcpErrorMessage(
        `删除MCP服务器失败: ${error.response?.data?.error || error.message}`
      );
    } finally {
      setLoadingMcpServers(false);
    }
  };

  // 滚动到最新消息
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 处理角色选择
  const handleRoleSelected = (roleData) => {
    setCurrentRole(roleData);
    setRoleSelected(true);
    setRoleModalVisible(false);
  };

  // 发送消息
  const sendMessage = async () => {
    if (!messageInput.trim()) return;

    const userMessage = messageInput.trim();
    setMessageInput("");

    // 添加用户消息到列表
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    setLoading(true);

    try {
      // 使用选定的模型发送请求
      const response = await api.post("/api/chat", {
        message: userMessage,
        model: selectedModel, // 添加模型参数
        web_search: webSearchEnabled, // 添加联网参数
      });

      if (response.data.message) {
        // 检查是否有联网搜索结果
        const hasSearchResults =
          response.data.search_results &&
          response.data.search_results.length > 0;

        // 添加AI回复到列表，包含搜索结果信息
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: response.data.message,
            search_results: hasSearchResults
              ? response.data.search_results
              : null,
          },
        ]);
      }
    } catch (error) {
      console.error("发送消息失败:", error);
      message.error(
        "发送消息失败: " + (error.response?.data?.error || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  // 处理按键事件
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 清除对话
  const clearConversation = async () => {
    try {
      await api.post("/api/conversations/clear");
      setMessages([]);
      message.success("对话已清除");
    } catch (error) {
      console.error("清除对话失败:", error);
      message.error(
        "清除对话失败: " + (error.response?.data?.error || error.message)
      );
    }
  };

  // 保存对话
  const saveConversation = async () => {
    try {
      const response = await api.post("/api/conversations", {
        title: saveTitle || undefined
      });

      if (response.data.success) {
        message.success("对话已保存");
        setSaveModalVisible(false);
        setSaveTitle("");

        // 刷新对话列表
        loadConversationList();
      } else {
        message.error("保存对话失败: " + (response.data.error || "未知错误"));
      }
    } catch (error) {
      message.error("保存对话失败: " + (error.response?.data?.error || error.message));
    }
  };

  // 加载对话列表
  const loadConversationList = async () => {
    setLoadingConversations(true);

    try {
      const response = await api.get("/api/conversations");
      setConversations(response.data);
    } catch (error) {
      console.error("加载对话列表失败:", error);
      message.error(
        "加载对话列表失败: " + (error.response?.data?.error || error.message)
      );
    } finally {
      setLoadingConversations(false);
    }
  };

  // 加载特定对话
  const loadConversation = async (filename) => {
    try {
      const response = await api.get(`/api/conversations/${filename}`);

      if (response.data.messages) {
        setMessages(response.data.messages);

        // 更新当前角色
        if (response.data.current_role) {
          // 如果后端返回了当前角色，更新前端状态
          const roleData = {
            role: response.data.current_role,
            system_content: response.data.messages[0]?.content || "",
          };
          setCurrentRole(roleData);
          setRoleSelected(true);
        }

        setDrawerVisible(false);
        message.success("对话已加载");
      }
    } catch (error) {
      console.error("加载对话失败:", error);
      message.error(
        "加载对话失败: " + (error.response?.data?.error || error.message)
      );
    }
  };

  // 删除对话
  const deleteConversation = async (filename) => {
    try {
      const response = await api.delete(`/api/conversations/${filename}`);

      if (response.data.success) {
        message.success("对话已删除");
        // 重新加载对话列表
        loadConversationList();
      }
    } catch (error) {
      console.error("删除对话失败:", error);
      message.error(
        "删除对话失败: " + (error.response?.data?.error || error.message)
      );
    }
  };

  // 生成图像
  const generateImage = async () => {
    if (!imagePrompt.trim()) return;

    setGeneratingImage(true);
    setImageUrl("");
    setRevisedPrompt("");

    try {
      // 使用DALL-E 3 API
      const response = await api.post("/api/image", {
        model: imageModel,
        prompt: imagePrompt,
        size: imageSize,
        quality: imageQuality,
        style: imageStyle,
        n: 1,
      });

      if (response.data.url) {
        setImageUrl(response.data.url);
        // 如果有修改后的提示词，显示它
        if (response.data.revised_prompt) {
          setRevisedPrompt(response.data.revised_prompt);
        }
      }
    } catch (error) {
      console.error("生成图像失败:", error);
      message.error(
        "生成图像失败: " + (error.response?.data?.error || error.message)
      );
    } finally {
      setGeneratingImage(false);
    }
  };

  // 打开抽屉时加载对话列表
  useEffect(() => {
    if (drawerVisible) {
      loadConversationList();
    }
  }, [drawerVisible]);

  // 打开MCP模态框时加载服务器列表
  useEffect(() => {
    if (mcpModalVisible) {
      loadMcpServers();
    }
  }, [mcpModalVisible]);

  // 获取角色名称显示
  const getRoleDisplayName = () => {
    if (!currentRole) return "未选择";

    const roleNames = {
      assistant: "美团AI助手",
      programmer: "程序员",
      teacher: "教师",
      creative: "创意顾问",
      custom: "自定义角色",
    };

    return roleNames[currentRole.role] || currentRole.role;
  };

  // 获取用户头像颜色
  const getUserAvatarColor = () => {
    return "#1890ff"; // 蓝色
  };

  // 获取AI头像颜色
  const getAIAvatarColor = () => {
    return "#52c41a"; // 绿色
  };

  // 在聊天头部添加联网状态显示
  useEffect(() => {
    // 当模型变更时，检查是否支持联网
    const currentModel = availableModels.find(
      (model) => model.value === selectedModel
    );
    if (!currentModel?.hasInternet && webSearchEnabled) {
      setWebSearchEnabled(false);
      message.info("当前模型不支持联网，已自动关闭联网功能");
    }
  }, [selectedModel, webSearchEnabled]);

  // 获取MCP服务器状态颜色
  const getMcpStatusColor = (status) => {
    switch (status) {
      case "connected":
        return "green";
      case "connecting":
        return "blue";
      case "disconnecting":
        return "orange";
      case "failed":
        return "red";
      default:
        return "default";
    }
  };

  // 获取MCP服务器状态文本
  const getMcpStatusText = (status) => {
    switch (status) {
      case "connected":
        return "已连接";
      case "connecting":
        return "连接中";
      case "disconnecting":
        return "断开中";
      case "failed":
        return "连接失败";
      default:
        return "未连接";
    }
  };

  return (
    <Layout className="app-container">
      <Header className="app-header">
        <div className="header-left">
          <Button
            type="text"
            icon={<MenuOutlined />}
            onClick={() => setDrawerVisible(true)}
            className="menu-button"
          />
          <h1 className="app-title">美团AI Agent</h1>
        </div>
        <div className="header-right">
          {/* 添加模型选择器 */}
          <Select
            value={selectedModel}
            onChange={setSelectedModel}
            style={{ width: 280 }}
            disabled={!apiConnected}
            optionLabelProp="label"
            dropdownMatchSelectWidth={false}
            dropdownStyle={{ width: 400, maxWidth: "80vw" }}
          >
            {availableModels.map((model) => (
              <Option key={model.value} value={model.value} label={model.label}>
                <div className="model-option">
                  <div className="model-name">{model.label}</div>
                  <div className="model-description">
                    {model.description}
                    {model.hasInternet && (
                      <span className="model-internet-badge">支持联网</span>
                    )}
                  </div>
                </div>
              </Option>
            ))}
          </Select>

          {/* 添加联网开关 */}
          <Button
            type={webSearchEnabled ? "primary" : "default"}
            icon={<GlobalOutlined />}
            onClick={() => setWebSearchEnabled(!webSearchEnabled)}
            className="web-search-button"
            disabled={
              !apiConnected ||
              !availableModels.find((model) => model.value === selectedModel)
                ?.hasInternet
            }
            title={
              !availableModels.find((model) => model.value === selectedModel)
                ?.hasInternet
                ? "当前模型不支持联网"
                : webSearchEnabled
                ? "关闭联网"
                : "开启联网"
            }
          >
            {webSearchEnabled ? "联网已开启" : "联网"}
          </Button>

          {/* 添加MCP按钮 */}
          <Button
            type="text"
            icon={<ApiOutlined />}
            onClick={() => setMcpModalVisible(true)}
            className="mcp-button"
            disabled={!apiConnected}
            title="模型上下文协议(MCP)服务"
          >
            MCP服务
          </Button>

          <Button
            type="text"
            icon={<UserSwitchOutlined />}
            onClick={() => setRoleModalVisible(true)}
            className="role-button"
            disabled={!apiConnected}
          >
            {currentRole ? getRoleDisplayName() : "选择角色"}
          </Button>
          <Button
            type="text"
            icon={<FileImageOutlined />}
            onClick={() => setImageModalVisible(true)}
            className="image-button"
            disabled={!apiConnected}
          >
            生成图像
          </Button>
          <Button
            type="text"
            icon={<ClearOutlined />}
            onClick={clearConversation}
            className="clear-button"
            disabled={!apiConnected}
          >
            清除对话
          </Button>
          <Button
            type="text"
            icon={<SaveOutlined />}
            onClick={() => setSaveModalVisible(true)}
            className="save-button"
            disabled={!apiConnected}
          >
            保存对话
          </Button>
        </div>
      </Header>

      <Content className="app-content">
        {apiChecking ? (
          <div className="api-checking">
            <Spin tip="正在连接API服务器..." />
          </div>
        ) : !apiConnected ? (
          <Alert
            message="API服务器连接失败"
            description="无法连接到API服务器，请确保API服务器已启动（端口5001）。"
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        ) : !roleSelected && !messages.length ? (
          <div className="role-selector-container">
            <RoleSelector
              onRoleSelected={handleRoleSelected}
              apiBaseUrl={apiBaseUrl}
            />
          </div>
        ) : (
          <>
            <div className="chat-header">
              <span>
                当前角色:{" "}
                <span className="current-role-name">
                  {getRoleDisplayName()}
                </span>
              </span>
              <span>
                当前模型:{" "}
                <span className="current-model-name">{selectedModel}</span>
              </span>
              {availableModels.find((model) => model.value === selectedModel)
                ?.hasInternet && (
                <span
                  className={`web-search-status ${
                    webSearchEnabled ? "enabled" : ""
                  }`}
                >
                  <GlobalOutlined />
                  {webSearchEnabled ? "联网已开启" : "联网已关闭"}
                </span>
              )}
              {/* 添加MCP状态显示 */}
              {mcpServers.some((server) => server.status === "connected") && (
                <span className="mcp-status enabled">
                  <ApiOutlined />
                  MCP服务已连接
                </span>
              )}
              <Button
                type="link"
                onClick={() => setRoleModalVisible(true)}
                className="change-role-button"
              >
                更换角色
              </Button>
            </div>

            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <h2>欢迎使用美团AI Agent</h2>
                  <p>基于FRIDAY大模型平台</p>
                  <p>输入消息开始对话</p>
                  {apiBaseUrl && (
                    <p className="api-info">API服务器: {apiBaseUrl}</p>
                  )}
                </div>
              ) : (
                messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`message-row ${
                      msg.role === "user"
                        ? "user-message-row"
                        : "ai-message-row"
                    }`}
                  >
                    {msg.role !== "user" && (
                      <Avatar
                        icon={<RobotOutlined />}
                        style={{ backgroundColor: getAIAvatarColor() }}
                        className="message-avatar"
                      />
                    )}
                    <div
                      className={`message-bubble ${
                        msg.role === "user"
                          ? "user-message-bubble"
                          : "ai-message-bubble"
                      }`}
                    >
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                      {msg.search_results && (
                        <div className="search-source">
                          <span className="search-source-title">
                            联网搜索来源:
                          </span>
                          {msg.search_results.map((result, idx) => (
                            <div key={idx} className="search-source-item">
                              {result.title || result.url}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    {msg.role === "user" && (
                      <Avatar
                        style={{ backgroundColor: getUserAvatarColor() }}
                        className="message-avatar"
                      >
                        您
                      </Avatar>
                    )}
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          </>
        )}

        <div className="input-container">
          <Button
            type="text"
            icon={<PlusCircleOutlined />}
            onClick={clearConversation}
            className="new-chat-button"
            title="新建会话"
            disabled={loading || !apiConnected || apiChecking}
          />
          <TextArea
            value={messageInput}
            onChange={(e) => setMessageInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              !roleSelected && !messages.length
                ? "请先选择AI角色..."
                : "输入消息..."
            }
            autoSize={{ minRows: 1, maxRows: 6 }}
            disabled={
              loading ||
              !apiConnected ||
              apiChecking ||
              (!roleSelected && !messages.length)
            }
          />
          <Button
            type="primary"
            icon={loading ? <LoadingOutlined /> : <SendOutlined />}
            onClick={sendMessage}
            disabled={
              !messageInput.trim() ||
              loading ||
              !apiConnected ||
              apiChecking ||
              (!roleSelected && !messages.length)
            }
            className="send-button"
          >
            发送
          </Button>
        </div>
      </Content>

      <Footer className="app-footer">
        AI Agent Webnew Date().getFullYear 基于FRIDAY大模型平台
      </Footer>

      {/* 对话列表抽屉 */}
      <Drawer
        title="保存的对话"
        placement="left"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={300}
      >
        <Spin spinning={loadingConversations}>
          {conversations.length === 0 ? (
            <div className="empty-conversations">
              <p>没有保存的对话</p>
            </div>
          ) : (
            <List
              dataSource={conversations}
              renderItem={(item) => (
                <List.Item
                  onClick={() => loadConversation(item.filename)}
                  className="conversation-item"
                  actions={[
                    <Popconfirm
                      title="删除对话"
                      description="确定要删除这个对话吗？此操作不可恢复。"
                      onConfirm={(e) => {
                        e.stopPropagation(); // 阻止事件冒泡，避免触发loadConversation
                        deleteConversation(item.filename);
                      }}
                      okText="确定"
                      cancelText="取消"
                      onCancel={(e) => e.stopPropagation()} // 阻止事件冒泡
                    >
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={(e) => e.stopPropagation()} // 阻止事件冒泡
                      />
                    </Popconfirm>,
                  ]}
                >
                  <div>
                    <div className="conversation-title">{item.title}</div>
                    <div className="conversation-date">{item.date}</div>
                  </div>
                </List.Item>
              )}
            />
          )}
        </Spin>
      </Drawer>

      {/* 保存对话模态框 */}
      <Modal
        title="保存对话"
        open={saveModalVisible}
        onOk={saveConversation}
        onCancel={() => setSaveModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item label="对话标题">
            <Input
              placeholder="输入标题（可选）"
              value={saveTitle}
              onChange={(e) => setSaveTitle(e.target.value)}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* MCP服务器管理模态框 */}
      <Modal
        title="MCP服务器管理"
        open={mcpModalVisible}
        onCancel={() => setMcpModalVisible(false)}
        footer={[
          <Button
            key="refresh"
            onClick={loadMcpServers}
            disabled={loadingMcpServers}
          >
            刷新
          </Button>,
          <Button
            key="add"
            type="primary"
            onClick={() => setMcpAddModalVisible(true)}
          >
            添加服务器
          </Button>,
          <Button key="close" onClick={() => setMcpModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={700}
      >
        <Spin spinning={loadingMcpServers}>
          {mcpErrorMessage && (
            <Alert
              message="错误"
              description={mcpErrorMessage}
              type="error"
              showIcon
              style={{ marginBottom: 16 }}
              closable
              onClose={() => setMcpErrorMessage("")}
            />
          )}

          {mcpServers.length === 0 ? (
            <div className="empty-mcp-servers">
              <p>没有配置MCP服务器</p>
              <p>点击"添加服务器"按钮添加MCP服务器</p>
            </div>
          ) : (
            <List
              dataSource={mcpServers}
              renderItem={(server) => (
                <List.Item
                  className="mcp-server-item"
                  actions={[
                    server.status === "connected" ? (
                      <Button
                        icon={<DisconnectOutlined />}
                        onClick={() => disconnectFromMcpServer(server.id)}
                        loading={mcpConnecting[server.id]}
                        danger
                      >
                        断开连接
                      </Button>
                    ) : (
                      <Button
                        icon={<LinkOutlined />}
                        onClick={() => connectToMcpServer(server.id)}
                        loading={mcpConnecting[server.id]}
                        type="primary"
                      >
                        连接
                      </Button>
                    ),
                    <Popconfirm
                      title="删除服务器"
                      description="确定要删除这个MCP服务器吗？此操作不可恢复。"
                      onConfirm={() => deleteMcpServer(server.id)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button type="text" danger icon={<DeleteOutlined />} />
                    </Popconfirm>,
                  ]}
                >
                  <div className="mcp-server-info">
                    <div className="mcp-server-name">
                      <Badge status={getMcpStatusColor(server.status)} />
                      <span>{server.id}</span>
                    </div>
                    <div className="mcp-server-status">
                      状态: {getMcpStatusText(server.status)}
                    </div>
                  </div>
                </List.Item>
              )}
            />
          )}
        </Spin>
      </Modal>

      {/* 添加MCP服务器模态框 */}
      <Modal
        title="添加MCP服务器"
        open={mcpAddModalVisible}
        onOk={addMcpServer}
        onCancel={() => setMcpAddModalVisible(false)}
        okText="添加"
        cancelText="取消"
      >
        <Form layout="vertical">
          <Form.Item
            label="服务器ID"
            required
            tooltip="服务器的唯一标识符，例如：amap-amap-sse"
          >
            <Input
              placeholder="输入服务器ID"
              value={newMcpServer.id}
              onChange={(e) =>
                setNewMcpServer((prev) => ({ ...prev, id: e.target.value }))
              }
            />
          </Form.Item>
          <Form.Item
            label="服务器URL"
            required
            tooltip="MCP服务器的URL地址，例如：https://mcp.amap.com/sse?key=your_key"
          >
            <Input
              placeholder="输入服务器URL"
              value={newMcpServer.config.url}
              onChange={(e) =>
                setNewMcpServer((prev) => ({
                  ...prev,
                  config: { ...prev.config, url: e.target.value },
                }))
              }
            />
          </Form.Item>
          <Alert
            message="提示"
            description="MCP服务器需要支持SSE (Server-Sent Events) 协议。如果服务器需要API密钥，请将其包含在URL中。"
            type="info"
            showIcon
          />
        </Form>
      </Modal>

      {/* 图像生成模态框 */}
      <Modal
        title="生成图像"
        open={imageModalVisible}
        onOk={() => {
          imageForm.validateFields().then(() => {
            generateImage();
          });
        }}
        onCancel={() => {
          setImageModalVisible(false);
          setImagePrompt("");
          setImageUrl("");
          setRevisedPrompt("");
        }}
        okText="生成"
        cancelText="取消"
        okButtonProps={{ loading: generatingImage }}
        width={700}
      >
        <Form form={imageForm} layout="vertical">
          <Form.Item
            label="图像描述"
            name="prompt"
            rules={[{ required: true, message: "请输入图像描述" }]}
          >
            <TextArea
              placeholder="描述您想要生成的图像..."
              autoSize={{ minRows: 3, maxRows: 6 }}
              value={imagePrompt}
              onChange={(e) => setImagePrompt(e.target.value)}
              maxLength={1000}
              showCount
            />
          </Form.Item>

          <Form.Item label="图像模型" name="model" initialValue="dall-e-3">
            <Radio.Group
              value={imageModel}
              onChange={(e) => setImageModel(e.target.value)}
            >
              <Radio.Button value="dall-e-3">DALL-E 3</Radio.Button>
            </Radio.Group>
          </Form.Item>

          <Form.Item label="图像尺寸" name="size" initialValue="1024x1024">
            <Radio.Group
              value={imageSize}
              onChange={(e) => setImageSize(e.target.value)}
            >
              <Radio.Button value="1024x1024">正方形 (1024x1024)</Radio.Button>
              <Radio.Button value="1792x1024">横向 (1792x1024)</Radio.Button>
              <Radio.Button value="1024x1792">纵向 (1024x1792)</Radio.Button>
            </Radio.Group>
          </Form.Item>

          <Form.Item label="图像质量" name="quality" initialValue="standard">
            <Radio.Group
              value={imageQuality}
              onChange={(e) => setImageQuality(e.target.value)}
            >
              <Radio.Button value="standard">标准</Radio.Button>
              <Radio.Button value="hd">高清</Radio.Button>
            </Radio.Group>
          </Form.Item>

          <Form.Item label="图像风格" name="style" initialValue="vivid">
            <Radio.Group
              value={imageStyle}
              onChange={(e) => setImageStyle(e.target.value)}
            >
              <Radio.Button value="vivid">生动 (Vivid)</Radio.Button>
              <Radio.Button value="natural">自然 (Natural)</Radio.Button>
            </Radio.Group>
          </Form.Item>

          {imageUrl && (
            <div className="generated-image">
              <img src={imageUrl} alt="生成的图像" />
              {revisedPrompt && (
                <div className="revised-prompt">
                  <div className="revised-prompt-title">AI修改后的提示词:</div>
                  <div className="revised-prompt-content">{revisedPrompt}</div>
                </div>
              )}
            </div>
          )}
        </Form>
      </Modal>

      {/* 角色选择模态框 */}
      <Modal
        title={
          <div className="role-modal-title">
            <span>选择AI角色</span>
            <span className="role-modal-subtitle">
              （可以删除自定义角色或保存新角色）
            </span>
          </div>
        }
        open={roleModalVisible}
        onCancel={() => setRoleModalVisible(false)}
        footer={null}
        width={700}
      >
        <RoleSelector
          onRoleSelected={handleRoleSelected}
          apiBaseUrl={apiBaseUrl}
        />
      </Modal>
    </Layout>
  );
}

export default App;
