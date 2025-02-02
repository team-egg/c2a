import React from 'react';
import { createStyles } from 'antd-style';

const useStyles = createStyles(({ css }) => ({
  wrapper: css``,
}));

const Base = () => {
  const { styles } = useStyles();

  return <div className={styles.wrapper}>Title</div>;
};

export default Base;
