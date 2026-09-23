from core.task import Task


class CommandParser:
    """
    يحول أمر المستخدم إلى Task.

    الصيغ المدعومة حاليًا:

    Coding:
        create file <path>
        create project <name>
        run <path>
        read <path>
        delete <path>
        write <path> | <content>
        append <path> | <content>
        list

    Memory:
        memory health_check
        memory save <memory_type> <key> <value>
        memory get <memory_type> <key>
        memory get_entry <memory_type> <key>
        memory search <query>
        memory list [memory_type]
        memory delete <memory_type> <key>
        memory clear_session <session_id>
        memory count [memory_type]
    """

    def parse(self, command: str) -> Task:

        command = command.strip()

        if not command:
            return Task(
                task_type="unknown",
                command=command,
            )

        lower = command.lower()

        # --------------------------------------------------
        # Memory
        # --------------------------------------------------

        if lower.startswith("memory "):

            body = command[len("memory "):].strip()

            if not body:
                return Task(
                    task_type="memory",
                    command=command,
                    data={},
                )

            parts = body.split()
            operation = parts[0].lower()

            data = {
                "operation": operation,
            }

            # -----------------------------
            # health_check
            # -----------------------------

            if operation == "health_check":
                return Task(
                    task_type="memory",
                    command=command,
                    data=data,
                )

            # -----------------------------
            # save
            # memory save <type> <key> <value>
            # -----------------------------

            if operation == "save":

                if len(parts) >= 4:

                    data.update(
                        {
                            "memory_type": parts[1],
                            "key": parts[2],
                            "value": " ".join(parts[3:]),
                        }
                    )

                return Task(
                    task_type="memory",
                    command=command,
                    data=data,
                )

            # -----------------------------
            # get
            # memory get <type> <key>
            # -----------------------------

            if operation == "get":

                if len(parts) >= 3:

                    data.update(
                        {
                            "memory_type": parts[1],
                            "key": parts[2],
                        }
                    )

                return Task(
                    task_type="memory",
                    command=command,
                    data=data,
                )

            # -----------------------------
            # get_entry
            # memory get_entry <type> <key>
            # -----------------------------

            if operation == "get_entry":

                if len(parts) >= 3:

                    data.update(
                        {
                            "memory_type": parts[1],
                            "key": parts[2],
                        }
                    )

                return Task(
                    task_type="memory",
                    command=command,
                    data=data,
                )

            # -----------------------------
            # search
            # memory search <query>
            # -----------------------------

            if operation == "search":

                data["query"] = " ".join(parts[1:])

                return Task(
                    task_type="memory",
                    command=command,
                    data=data,
                )

            # -----------------------------
            # list
            # memory list [memory_type]
            # -----------------------------

            if operation == "list":

                if len(parts) >= 2:
                    data["memory_type"] = parts[1]

                return Task(
                    task_type="memory",
                    command=command,
                    data=data,
                )

            # -----------------------------
            # delete
            # memory delete <type> <key>
            # -----------------------------

            if operation == "delete":

                if len(parts) >= 3:

                    data.update(
                        {
                            "memory_type": parts[1],
                            "key": parts[2],
                        }
                    )

                return Task(
                    task_type="memory",
                    command=command,
                    data=data,
                )

            # -----------------------------
            # clear_session
            # memory clear_session <session_id>
            # -----------------------------

            if operation == "clear_session":

                if len(parts) >= 2:
                    data["session_id"] = parts[1]

                return Task(
                    task_type="memory",
                    command=command,
                    data=data,
                )

            # -----------------------------
            # count
            # memory count [memory_type]
            # -----------------------------

            if operation == "count":

                if len(parts) >= 2:
                    data["memory_type"] = parts[1]

                return Task(
                    task_type="memory",
                    command=command,
                    data=data,
                )

            # -----------------------------
            # Unsupported memory operation
            # -----------------------------

            return Task(
                task_type="memory",
                command=command,
                data=data,
            )

        # --------------------------------------------------
        # Browser and Computer operations
        # --------------------------------------------------

        if lower.startswith("browser "):
            return Task(
                task_type="browser",
                command=command,
            )

        if lower.startswith("computer "):
            return Task(
                task_type="computer",
                command=command,
            )

        # --------------------------------------------------
        # Service-only capability operations
        # --------------------------------------------------

        capability_prefixes = (
            ("research", ("research ", "\u0627\u0628\u062d\u062b ", "\u0628\u062d\u062b ")),
            ("analyze", ("analyze ", "\u062d\u0644\u0644 ", "\u062a\u062d\u0644\u064a\u0644 ")),
            ("plan", ("plan ", "\u062e\u0637\u0637 ", "\u062e\u0637\u0629 ")),
            ("content", ("content ", "\u0645\u062d\u062a\u0648\u0649 ", "\u0623\u0646\u0634\u0626 \u0645\u062d\u062a\u0648\u0649 ")),
            ("video", ("video ", "\u0641\u064a\u062f\u064a\u0648 ", "\u0623\u0646\u0634\u0626 \u0641\u064a\u062f\u064a\u0648 ")),
            ("audio", ("audio ", "\u0635\u0648\u062a ")),
            ("media", ("media ", "\u0648\u0633\u0627\u0626\u0637 ")),
            ("asset", ("asset ", "\u0623\u0635\u0644 ")),
            ("product", ("product ", "\u0645\u0646\u062a\u062c ")),
            ("policy", ("policy ", "\u0633\u064a\u0627\u0633\u0629 ")),
            ("monitor", ("monitor ", "\u0631\u0627\u0642\u0628 ")),
            ("diagnose", ("diagnose ", "\u0634\u062e\u0651\u0635 ", "\u0634\u062e\u0635 ")),
            ("experiment", ("experiment ", "\u062a\u062c\u0631\u0628\u0629 ")),
            ("publishing", ("publish ", "publishing ", "\u0646\u0634\u0631 ")),
            ("image", ("image ", "\u0635\u0648\u0631\u0629 ")),
        )
        for task_type, prefixes in capability_prefixes:
            if any(lower.startswith(prefix.lower()) for prefix in prefixes):
                return Task(
                    task_type=task_type,
                    command=command,
                )

        # --------------------------------------------------
        # Coding
        # --------------------------------------------------

        coding_keywords = (

            # إنشاء ملف
            "أنشئ ملف",
            "انشئ ملف",
            "create file",

            # إنشاء مشروع
            "أنشئ مشروع",
            "انشئ مشروع",
            "create project",

            # تشغيل
            "شغل",
            "run",

            # قراءة
            "اقرأ",
            "read",

            # حذف
            "احذف",
            "delete",

            # كتابة
            "write",

            # إضافة
            "append",

            # عرض الملفات
            "list",

            # كلمات عامة
            "برنامج",
            "بايثون",
            "python",
            "ملف",
        )

        if any(
            lower.startswith(keyword.lower())
            for keyword in coding_keywords
        ):
            return Task(
                task_type="coding",
                command=command,
            )

        # --------------------------------------------------
        # Unknown
        # --------------------------------------------------

        return Task(
            task_type="unknown",
            command=command,
        )
