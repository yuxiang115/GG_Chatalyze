const express = require('express');
const dotaConstants = require('dotaconstants');
const app = express();
const availableKeys = Object.keys(dotaConstants);

app.get('/api/data', (req, res) => {
  const { type } = req.query;

  if (!type) {
    return res.status(400).json({
      error: 'Parameter "type" is required. Example: ?type=heroes',
      availableTypes: availableKeys,
    });
  }

  if (!availableKeys.includes(type)) {
    return res.status(404).json({
      error: `Type "${type}" not found.`,
      availableTypes: availableKeys,
    });
  }

  // 返回指定类型的数据
  const data = dotaConstants[type];
  return res.json(data);
});

// 新增的列表 API，返回所有数据类型的名称
app.get('/api/list', (req, res) => {
  return res.json({
    availableTypes: availableKeys,
  });
});

// 启动服务
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Dotaconstants API running on http://localhost:${PORT}`);
});