export async function copyTextToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // Fallback will be used below.
  }

  try {
    const textArea = document.createElement('textarea');

    textArea.value = text;
    textArea.setAttribute('readonly', 'true');
    textArea.style.position = 'fixed';
    textArea.style.left = '-9999px';
    textArea.style.top = '-9999px';

    document.body.appendChild(textArea);
    textArea.select();

    const copied = document.execCommand('copy');

    document.body.removeChild(textArea);

    return copied;
  } catch {
    return false;
  }
}