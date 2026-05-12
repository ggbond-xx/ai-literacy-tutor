export function getApiErrorMessage(error, fallbackMessage) {
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail) && detail.length) {
    return detail
      .map((item) => {
        const field = Array.isArray(item.loc) ? item.loc[item.loc.length - 1] : "field";
        if (field === "password" && item.msg.includes("at least 4")) {
          return "密码至少需要 4 位字符。";
        }
        if (field === "username" && item.msg.includes("at least 3")) {
          return "用户名至少需要 3 位字符。";
        }
        return item.msg;
      })
      .join("；");
  }

  if (typeof detail === "string" && detail.trim()) {
    if (detail.includes("Username already exists")) {
      return "用户名已存在，请更换一个新的账号名。";
    }
    return detail;
  }

  return fallbackMessage;
}
