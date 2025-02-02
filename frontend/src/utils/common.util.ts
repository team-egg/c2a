// 判断是否是json字符串
export function isJSONString(str: string): boolean {
  try {
    const parsed = JSON.parse(str);
    return typeof parsed === 'object';
  } catch (e) {
    return false;
  }
}
