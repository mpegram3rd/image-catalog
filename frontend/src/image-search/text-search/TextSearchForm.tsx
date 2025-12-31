import {Box, TextInput} from "@mantine/core";
import {useForm} from "@mantine/form";
import {IconUpload} from "@tabler/icons-react";

export default function TextSearchForm() {
    const form = useForm({
        mode: 'uncontrolled',
        initialValues: {
            searchText: ''
        },

        validate: {
            searchText: (value: string) => value.length > 0 ? null : 'You must enter a search term'
        }
    });

    return (
        <form className="text-search" onSubmit={form.onSubmit((values) => console.log(values))}>
            <Box
                mx="auto"
                w={400}
            >
                <TextInput
                    label="Search Text"
                    placeholder="Image Description"
                    key={form.key('searchText')}
                    {...form.getInputProps('searchText')}
                    color="var(--mantine-color-blue-6)"
                    rightSection={<IconUpload size={20} color="var(--mantine-color-blue-6)" />}
                />
                Drag and Drop an Image to find Similar ones
            </Box>
        </form>
    )
}