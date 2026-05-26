const express = require("express");

const {
  applyLeave,
  getMyLeaves,
  getPendingLeaves,
  updateLeaveStatus,
} = require("../controllers/leaveController");
const { protect, authorizeRoles } = require("../middleware/authMiddleware");

const router = express.Router();

router.post("/apply", protect, authorizeRoles("employee", "manager"), applyLeave);
router.get("/my-leaves", protect, getMyLeaves);
router.get("/pending", protect, authorizeRoles("manager"), getPendingLeaves);
router.put("/:id/status", protect, authorizeRoles("manager"), updateLeaveStatus);

module.exports = router;
