import React, { memo } from 'react';

interface IProps {
  name: string;
  width?: number;
  height?: number;
  prefix?: string;
  color?: string;
  className?: string;
  onClick?: () => void;
  style?: React.CSSProperties;
}

const SvgIcon = memo(
  ({ width, height, name, onClick, className = '', prefix = 'icon', color = '#333', ...rest }: IProps) => {
    const symbolId = `#${prefix}-${name}`;

    return (
      <svg className={className} width={width} height={height} {...rest} aria-hidden="true" onClick={onClick}>
        <use href={symbolId} fill={color} />
      </svg>
    );
  },
);

export default SvgIcon;
