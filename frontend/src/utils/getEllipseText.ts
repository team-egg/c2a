export const getEllipseText = (tokenAddress = '', startSize = 4, endSize = 4) => {
  if (tokenAddress.length < startSize + endSize) {
    return tokenAddress;
  }
  return tokenAddress.slice(0, startSize) + '...' + tokenAddress.slice(-endSize);
};
